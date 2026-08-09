import { DexieAdapter } from './dexie/DexieAdapter'
import type { StorageAdapter } from './StorageAdapter'

/**
 * Single import site for the storage layer (SPEC.md §1 rule 2). Swapping
 * to `SupabaseAdapter` (Milestone 16) later means changing this one line,
 * not any component.
 */
export const storage: StorageAdapter = new DexieAdapter()

export type { ExportBundle, StorageAdapter } from './StorageAdapter'
