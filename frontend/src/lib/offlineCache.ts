import { get, set, del, keys } from "idb-keyval";
import type { AskResponse, CachedAnswer, Equipment } from "../types";

const CACHE_PREFIX = "fieldtech:";
const EQUIPMENT_KEY = `${CACHE_PREFIX}active_equipment`;
const ANSWERS_KEY = `${CACHE_PREFIX}answers`;

export async function cacheEquipment(eq: Equipment): Promise<void> {
  await set(EQUIPMENT_KEY, eq);
}

export async function getCachedEquipment(): Promise<Equipment | null> {
  return (await get(EQUIPMENT_KEY)) ?? null;
}

export async function cacheAnswer(
  question: string,
  response: AskResponse,
  equipmentId?: string
): Promise<void> {
  const entry: CachedAnswer = {
    id: crypto.randomUUID(),
    question,
    response,
    equipment_id: equipmentId,
    cached_at: Date.now(),
  };
  const list: CachedAnswer[] = (await get(ANSWERS_KEY)) ?? [];
  list.unshift(entry);
  await set(ANSWERS_KEY, list.slice(0, 50));
}

export async function getCachedAnswers(): Promise<CachedAnswer[]> {
  return (await get(ANSWERS_KEY)) ?? [];
}

export async function findCachedAnswer(
  question: string,
  equipmentId?: string
): Promise<CachedAnswer | null> {
  const list = await getCachedAnswers();
  const q = question.toLowerCase().trim();
  return (
    list.find(
      (a) =>
        a.question.toLowerCase().trim() === q &&
        (a.equipment_id ?? "") === (equipmentId ?? "")
    ) ?? null
  );
}

export async function clearOfflineCache(): Promise<void> {
  const allKeys = await keys();
  for (const k of allKeys) {
    if (String(k).startsWith(CACHE_PREFIX)) await del(k);
  }
}
