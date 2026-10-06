import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Play, Pause, Layers, Sparkles } from "lucide-react";

export function ThreeHeroScene() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isRotating, setIsRotating] = useState(true);
  const [wireframeMode, setWireframeMode] = useState(false);

  const animStateRef = useRef({
    isRotating: true,
    wireframeMode: false,
    mouseX: 0,
    mouseY: 0,
    targetRotationX: 0,
    targetRotationY: 0,
    burstTime: 0,
  });

  useEffect(() => {
    animStateRef.current.isRotating = isRotating;
  }, [isRotating]);

  useEffect(() => {
    animStateRef.current.wireframeMode = wireframeMode;
  }, [wireframeMode]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Light-mode architectural scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f8f7);
    scene.fog = new THREE.Fog(0xf8f8f7, 8, 16);

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 450;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    container.appendChild(renderer.domElement);

    const vaultGroup = new THREE.Group();
    scene.add(vaultGroup);

    // 1. Central Core: Clean matte architectural crystalline polyhedron
    const coreGeo = new THREE.IcosahedronGeometry(1.6, 1);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0xfafafa,
      roughness: 0.2,
      metalness: 0.1,
      transparent: true,
      opacity: 0.9,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    vaultGroup.add(coreMesh);

    // Wireframe edges in graphite
    const wireGeo = new THREE.IcosahedronGeometry(1.61, 1);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x334155,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
    });
    const wireMesh = new THREE.Mesh(wireGeo, wireMat);
    vaultGroup.add(wireMesh);

    // 2. Delicate Gyroscopic Rings (Architectural balance)
    const ringGeo1 = new THREE.TorusGeometry(2.3, 0.012, 16, 120);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: 0x475569,
      transparent: true,
      opacity: 0.4,
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    vaultGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(2.7, 0.012, 16, 120);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x64748b,
      transparent: true,
      opacity: 0.3,
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    vaultGroup.add(ring2);

    // 3. Vector Embedding Point Constellation (Graphite slate particles)
    const particleCount = 280;
    const particlePositions = new Float32Array(particleCount * 3);
    const particleOriginals = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const radius = 2.4 + Math.random() * 2.8;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      particlePositions[i * 3] = x;
      particlePositions[i * 3 + 1] = y;
      particlePositions[i * 3 + 2] = z;

      particleOriginals[i * 3] = x;
      particleOriginals[i * 3 + 1] = y;
      particleOriginals[i * 3 + 2] = z;
    }

    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));

    const particleMat = new THREE.PointsMaterial({
      color: 0x475569,
      size: 0.07,
      transparent: true,
      opacity: 0.7,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    vaultGroup.add(particles);

    // Subtle connection lines between near nodes
    const lineIndices: number[] = [];
    let lineCount = 0;
    for (let i = 0; i < particleCount && lineCount < 70; i += 4) {
      for (let j = i + 1; j < particleCount && lineCount < 70; j += 5) {
        const dx = particlePositions[i * 3] - particlePositions[j * 3];
        const dy = particlePositions[i * 3 + 1] - particlePositions[j * 3 + 1];
        const dz = particlePositions[i * 3 + 2] - particlePositions[j * 3 + 2];
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (dist < 1.3) {
          lineIndices.push(i, j);
          lineCount++;
        }
      }
    }

    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute("position", particleGeo.getAttribute("position"));
    lineGeo.setIndex(lineIndices);

    const lineMat = new THREE.LineBasicMaterial({
      color: 0x94a3b8,
      transparent: true,
      opacity: 0.25,
    });
    const lines = new THREE.LineSegments(lineGeo, lineMat);
    vaultGroup.add(lines);

    // Architectural Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.8);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.4);
    dirLight1.position.set(5, 8, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xe2e8f0, 0.8);
    dirLight2.position.set(-5, -4, -3);
    scene.add(dirLight2);

    // Subtle Mouse Tracking & Orbit
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const handlePointerDown = (e: PointerEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const handlePointerMove = (e: PointerEvent) => {
      const rect = container.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      animStateRef.current.mouseX = nx;
      animStateRef.current.mouseY = ny;

      if (isDragging) {
        const deltaX = e.clientX - prevMouseX;
        const deltaY = e.clientY - prevMouseY;
        animStateRef.current.targetRotationY += deltaX * 0.005;
        animStateRef.current.targetRotationX += deltaY * 0.005;
        prevMouseX = e.clientX;
        prevMouseY = e.clientY;
      }
    };

    const handlePointerUp = () => {
      isDragging = false;
    };

    container.addEventListener("pointerdown", handlePointerDown);
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    let animId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      coreMat.wireframe = animStateRef.current.wireframeMode;

      if (animStateRef.current.isRotating) {
        vaultGroup.rotation.y += 0.003;
      }

      vaultGroup.rotation.y +=
        (animStateRef.current.targetRotationY + animStateRef.current.mouseX * 0.25 - vaultGroup.rotation.y) *
        0.05;
      vaultGroup.rotation.x +=
        (animStateRef.current.targetRotationX - animStateRef.current.mouseY * 0.25 - vaultGroup.rotation.x) *
        0.05;

      ring1.rotation.z = time * 0.08;
      ring2.rotation.x = time * 0.09;

      if (animStateRef.current.burstTime > 0) {
        const factor = 1 + Math.sin(animStateRef.current.burstTime * 4) * 0.25;
        const posAttr = particleGeo.getAttribute("position") as THREE.BufferAttribute;
        for (let i = 0; i < particleCount; i++) {
          posAttr.setXYZ(
            i,
            particleOriginals[i * 3] * factor,
            particleOriginals[i * 3 + 1] * factor,
            particleOriginals[i * 3 + 2] * factor,
          );
        }
        posAttr.needsUpdate = true;
        animStateRef.current.burstTime -= delta;
        if (animStateRef.current.burstTime <= 0) {
          animStateRef.current.burstTime = 0;
          for (let i = 0; i < particleCount; i++) {
            posAttr.setXYZ(
              i,
              particleOriginals[i * 3],
              particleOriginals[i * 3 + 1],
              particleOriginals[i * 3 + 2],
            );
          }
          posAttr.needsUpdate = true;
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      container.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);

      renderer.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      wireGeo.dispose();
      wireMat.dispose();
      ringGeo1.dispose();
      ringMat1.dispose();
      ringGeo2.dispose();
      ringMat2.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      lineGeo.dispose();
      lineMat.dispose();

      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  const triggerPulse = () => {
    animStateRef.current.burstTime = 1.0;
  };

  return (
    <div className="relative h-full w-full select-none overflow-hidden rounded-2xl border border-neutral-200/80 bg-[#f8f8f7]">
      <div ref={containerRef} className="h-full w-full cursor-grab active:cursor-grabbing" />

      {/* Understated, Calm Light Mode Controls */}
      <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-neutral-200/90 bg-white/90 px-3 py-1 shadow-sm backdrop-blur-md">
        <button
          onClick={() => setIsRotating(!isRotating)}
          className="flex items-center gap-1 text-[11px] font-medium text-neutral-700 hover:text-neutral-900 transition"
        >
          {isRotating ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
          <span>{isRotating ? "Pause" : "Spin"}</span>
        </button>

        <span className="text-neutral-300">·</span>

        <button
          onClick={() => setWireframeMode(!wireframeMode)}
          className="flex items-center gap-1 text-[11px] font-medium text-neutral-700 hover:text-neutral-900 transition"
        >
          <Layers className="h-3 w-3" />
          <span>Wireframe</span>
        </button>

        <span className="text-neutral-300">·</span>

        <button
          onClick={triggerPulse}
          className="flex items-center gap-1 text-[11px] font-medium text-neutral-700 hover:text-neutral-900 transition"
        >
          <Sparkles className="h-3 w-3 text-neutral-500" />
          <span>RRF Pulse</span>
        </button>
      </div>

      <div className="pointer-events-none absolute top-3 left-3 text-[10px] font-mono uppercase tracking-wider text-neutral-400">
        Local Vector Index Matrix
      </div>
    </div>
  );
}
