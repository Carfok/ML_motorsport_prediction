'use client';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function Circuit3D({ points }) {
    const mountRef = useRef(null);

    useEffect(() => {
        // Init Scene
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        mountRef.current.appendChild(renderer.domElement);

        // Geometría del Trazado (Visualización del Grafo GNN)
        const curve = new THREE.CatmullRomCurve3(
            points.map(p => new THREE.Vector3(p.x, p.y, p.z))
        );
        const geometry = new THREE.TubeGeometry(curve, 100, 0.1, 8, true);
        const material = new THREE.MeshNormalMaterial();
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        camera.position.z = 10;

        const animate = () => {
            requestAnimationFrame(animate);
            mesh.rotation.y += 0.005;
            renderer.render(scene, camera);
        };
        animate();

        return () => {
            mountRef.current && mountRef.current.removeChild(renderer.domElement);
        };
    }, [points]);

    return (
        <div ref={mountRef} className="w-full h-[500px] bg-slate-900 rounded-lg overflow-hidden border border-slate-700 shadow-2xl">
            {/* 3D Container render point */}
        </div>
    );
}
