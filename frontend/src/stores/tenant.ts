import { create } from "zustand";
import {
  getActiveOrgId,
  getActiveWorkspaceId,
  request,
  setActiveOrgId,
  setActiveWorkspaceId,
} from "../lib/api";
import type { Organization, OrgUsage, Workspace } from "../lib/types";

interface TenantState {
  organizations: Organization[];
  currentOrg: Organization | null;
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  usage: OrgUsage | null;
  loading: boolean;

  loadOrganizations: () => Promise<void>;
  selectOrganization: (orgId: string) => Promise<void>;
  loadWorkspaces: (orgId?: string) => Promise<void>;
  selectWorkspace: (workspaceId: string) => void;
  loadUsage: () => Promise<void>;
  createOrganization: (name: string) => Promise<Organization>;
  createWorkspace: (name: string, description?: string) => Promise<Workspace>;
}

export const useTenant = create<TenantState>((set, get) => ({
  organizations: [],
  currentOrg: null,
  workspaces: [],
  currentWorkspace: null,
  usage: null,
  loading: false,

  loadOrganizations: async () => {
    set({ loading: true });
    try {
      const orgs = await request<Organization[]>("/organizations");
      const savedOrgId = getActiveOrgId();
      const currentOrg = orgs.find((o) => o.id === savedOrgId) || orgs[0] || null;

      if (currentOrg) {
        setActiveOrgId(currentOrg.id);
      }

      set({ organizations: orgs, currentOrg, loading: false });

      if (currentOrg) {
        await get().loadWorkspaces(currentOrg.id);
        void get().loadUsage();
      }
    } catch {
      set({ organizations: [], currentOrg: null, loading: false });
    }
  },

  selectOrganization: async (orgId: string) => {
    const org = get().organizations.find((o) => o.id === orgId) || null;
    if (!org) return;

    setActiveOrgId(org.id);
    setActiveWorkspaceId(null);
    set({ currentOrg: org, currentWorkspace: null, workspaces: [] });

    await get().loadWorkspaces(org.id);
    void get().loadUsage();
    window.dispatchEvent(new Event("lda:tenant_changed"));
  },

  loadWorkspaces: async (orgId?: string) => {
    const targetOrgId = orgId || get().currentOrg?.id;
    if (!targetOrgId) return;

    try {
      const wsList = await request<Workspace[]>(`/organizations/${targetOrgId}/workspaces`);
      const savedWsId = getActiveWorkspaceId();
      const currentWorkspace = wsList.find((w) => w.id === savedWsId) || wsList[0] || null;

      if (currentWorkspace) {
        setActiveWorkspaceId(currentWorkspace.id);
      }

      set({ workspaces: wsList, currentWorkspace });
    } catch {
      set({ workspaces: [], currentWorkspace: null });
    }
  },

  selectWorkspace: (workspaceId: string) => {
    const ws = get().workspaces.find((w) => w.id === workspaceId) || null;
    if (!ws) return;

    setActiveWorkspaceId(ws.id);
    set({ currentWorkspace: ws });
    window.dispatchEvent(new Event("lda:tenant_changed"));
  },

  loadUsage: async () => {
    const orgId = get().currentOrg?.id;
    if (!orgId) return;

    try {
      const usage = await request<OrgUsage>(`/organizations/${orgId}/usage`);
      set({ usage });
    } catch {
      set({ usage: null });
    }
  },

  createOrganization: async (name: string) => {
    const newOrg = await request<Organization>("/organizations", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    await get().loadOrganizations();
    await get().selectOrganization(newOrg.id);
    return newOrg;
  },

  createWorkspace: async (name: string, description?: string) => {
    const orgId = get().currentOrg?.id;
    if (!orgId) throw new Error("No active organization");

    const newWs = await request<Workspace>(`/organizations/${orgId}/workspaces`, {
      method: "POST",
      body: JSON.stringify({ name, description }),
    });
    await get().loadWorkspaces(orgId);
    get().selectWorkspace(newWs.id);
    return newWs;
  },
}));
