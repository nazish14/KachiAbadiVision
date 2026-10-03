import type { DetectResult } from "../types/civic";
const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.2.2:8000";

export async function detectImage(uri: string, latitude?: number, longitude?: number): Promise<DetectResult> {
  const form = new FormData();
  form.append("file", { uri, name: "civic-image.jpg", type: "image/jpeg" } as unknown as Blob);
  if (latitude !== undefined && longitude !== undefined) {
    form.append("latitude", String(latitude));
    form.append("longitude", String(longitude));
  }
  const response = await fetch(`${API_URL}/api/v1/detect`, { method: "POST", body: form });
  if (!response.ok) throw new Error(`Detection failed (${response.status}): ${await response.text()}`);
  return response.json() as Promise<DetectResult>;
}
