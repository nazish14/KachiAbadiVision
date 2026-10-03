export type CivicCategory = "garbage_dump" | "pothole" | "open_manhole" | "damaged_lights";
export type Detection = { category: CivicCategory; confidence: number; bbox: [number, number, number, number] };
export type DetectResult = {
  report_id: string; image_width: number; image_height: number;
  detections: Detection[]; counts: Record<string, number>; severity: string;
  demo_mode: boolean; latitude?: number | null; longitude?: number | null;
  annotated_image_url?: string | null;
};
