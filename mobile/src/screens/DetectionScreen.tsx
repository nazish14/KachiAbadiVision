import React, { useState } from "react";
import { ActivityIndicator, Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as Location from "expo-location";
import { StatusBar } from "expo-status-bar";
import { detectImage } from "../services/api";
import type { DetectResult } from "../types/civic";

export default function DetectionScreen() {
  const [uri, setUri] = useState<string | null>(null);
  const [result, setResult] = useState<DetectResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function chooseImage(camera: boolean) {
    setError(""); setResult(null);
    const permission = camera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) { setError("Please allow camera or photo library access."); return; }
    const options: ImagePicker.ImagePickerOptions = { mediaTypes: ["images"], quality: 0.85 };
    const picked = camera
      ? await ImagePicker.launchCameraAsync(options)
      : await ImagePicker.launchImageLibraryAsync(options);
    if (picked.canceled || !picked.assets[0]) return;
    const imageUri = picked.assets[0].uri;
    setUri(imageUri);
    await submitImage(imageUri);
  }

  async function submitImage(imageUri: string) {
    setLoading(true); setError("");
    try {
      let latitude: number | undefined, longitude: number | undefined;
      const permission = await Location.requestForegroundPermissionsAsync();
      if (permission.granted) {
        try {
          const position = await Location.getCurrentPositionAsync({});
          latitude = position.coords.latitude; longitude = position.coords.longitude;
        } catch { /* GPS is optional. */ }
      }
      setResult(await detectImage(imageUri, latitude, longitude));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally { setLoading(false); }
  }

  return <View style={styles.root}>
    <StatusBar style="dark" />
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.eyebrow}>SMART CIVIC REPORTING</Text>
      <Text style={styles.title}>KachiAbadiVision</Text>
      <Text style={styles.subtitle}>Capture a street issue, review detections, and create a report.</Text>
      <View style={styles.actions}>
        <Pressable accessibilityRole="button" style={styles.primary} onPress={() => chooseImage(true)}>
          <Text style={styles.primaryText}>Open camera</Text>
        </Pressable>
        <Pressable accessibilityRole="button" style={styles.secondary} onPress={() => chooseImage(false)}>
          <Text style={styles.secondaryText}>Choose from gallery</Text>
        </Pressable>
      </View>
      {uri && <Image source={{ uri }} style={styles.preview} />}
      {loading && <View style={styles.loading}><ActivityIndicator size="large" color="#176B52" /><Text style={styles.muted}>Analyzing image…</Text></View>}
      {!!error && <Text accessibilityRole="alert" style={styles.error}>{error}</Text>}
      {result && <View style={styles.card}>
        <Text style={styles.cardTitle}>Detection summary</Text>
        <View style={styles.metricRow}><Text style={styles.metricLabel}>Severity</Text><Text style={styles.metricValue}>{result.severity}</Text></View>
        <View style={styles.metricRow}><Text style={styles.metricLabel}>Objects detected</Text><Text style={styles.metricValue}>{result.detections.length}</Text></View>
        {Object.entries(result.counts).length === 0
          ? <Text style={styles.muted}>No objects detected in this result.</Text>
          : Object.entries(result.counts).map(([name, count]) => <View key={name} style={styles.metricRow}>
              <Text style={styles.metricLabel}>{name.replaceAll("_", " ")}</Text><Text style={styles.metricValue}>{count}</Text>
            </View>)}
        {result.demo_mode && <Text style={styles.notice}>Demo mode: detections are synthetic and are not real AI findings.</Text>}
        <Text style={styles.reportId}>Report ID: {result.report_id}</Text>
      </View>}
      <Text style={styles.footer}>Location is optional. Confirm report details before sharing with authorities.</Text>
    </ScrollView>
  </View>;
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#F4F7F5" },
  container: { padding: 22, paddingTop: 42, gap: 16, flexGrow: 1 },
  eyebrow: { color: "#176B52", fontWeight: "700", letterSpacing: 1.4, fontSize: 11 },
  title: { fontSize: 30, fontWeight: "800", color: "#153D31" },
  subtitle: { fontSize: 15, lineHeight: 22, color: "#56665F" },
  actions: { gap: 10, marginTop: 4 },
  primary: { backgroundColor: "#176B52", padding: 16, borderRadius: 13 },
  primaryText: { color: "#FFFFFF", textAlign: "center", fontWeight: "700" },
  secondary: { borderWidth: 1, borderColor: "#176B52", padding: 15, borderRadius: 13 },
  secondaryText: { color: "#176B52", textAlign: "center", fontWeight: "700" },
  preview: { width: "100%", height: 280, borderRadius: 15, resizeMode: "contain", backgroundColor: "#E5EBE7" },
  loading: { alignItems: "center", gap: 10, padding: 18 },
  muted: { color: "#66736D", lineHeight: 20 },
  error: { color: "#B42318", backgroundColor: "#FEE4E2", padding: 12, borderRadius: 10 },
  card: { backgroundColor: "#FFFFFF", padding: 18, borderRadius: 16, gap: 12, borderWidth: 1, borderColor: "#E3EAE5" },
  cardTitle: { fontSize: 19, fontWeight: "800", color: "#153D31" },
  metricRow: { flexDirection: "row", justifyContent: "space-between", gap: 12 },
  metricLabel: { color: "#596760", textTransform: "capitalize", flexShrink: 1 },
  metricValue: { color: "#153D31", fontWeight: "700" },
  notice: { color: "#875A00", backgroundColor: "#FFF4CC", padding: 10, borderRadius: 9, lineHeight: 19 },
  reportId: { fontSize: 11, color: "#7A8780" },
  footer: { color: "#7A8780", fontSize: 12, lineHeight: 18, marginTop: 4, marginBottom: 20 }
});
