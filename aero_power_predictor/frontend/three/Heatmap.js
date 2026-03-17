export function calculateAeroHeatmap(telemetryData) {
    // Lógica para mapear carga aero a colores (R-G-B)
    return telemetryData.map(point => ({
        ...point,
        color: point.downforce > 0.8 ? 0xff0000 : 0x00ff00
    }));
}
