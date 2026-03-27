"use client";

import { useEffect, useState } from "react";
import {
  listEvents,
  createEvent,
  updateEvent,
  deleteEvent,
  getAuthStatus,
} from "@/lib/api";

type CalEvent = {
  id: string;
  summary: string;
  start: string;
  end: string;
  description?: string | null;
  location?: string | null;
};

const empty = { summary: "", start: "", end: "", description: "", location: "" };

export default function CalendarPage() {
  const [events, setEvents] = useState<CalEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState(empty);
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    getAuthStatus().then((d) => {
      if (d.connected.includes("google")) {
        setConnected(true);
      }
    });
  }, []);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listEvents();
      setEvents(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (connected) load();
  }, [connected]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateEvent(editingId, form);
      } else {
        await createEvent(form);
      }
      setForm(empty);
      setEditingId(null);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleEdit = (ev: CalEvent) => {
    setEditingId(ev.id);
    setForm({
      summary: ev.summary,
      start: ev.start,
      end: ev.end,
      description: ev.description || "",
      location: ev.location || "",
    });
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this event?")) return;
    try {
      await deleteEvent(id);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!connected) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Calendar</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
          Not connected to Google.{" "}
          <a href="/connections" className="text-blue-600 underline">
            Connect now
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Calendar</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Event form */}
      <form onSubmit={handleSubmit} className="bg-white border rounded-xl p-5 space-y-3">
        <h2 className="font-semibold">{editingId ? "Edit Event" : "New Event"}</h2>
        <input
          placeholder="Summary"
          value={form.summary}
          onChange={(e) => setForm({ ...form, summary: e.target.value })}
          className="w-full border rounded-lg px-3 py-2 text-sm"
          required
        />
        <div className="grid grid-cols-2 gap-3">
          <input
            type="datetime-local"
            value={form.start?.slice(0, 16) || ""}
            onChange={(e) => setForm({ ...form, start: e.target.value + ":00" })}
            className="border rounded-lg px-3 py-2 text-sm"
            required
          />
          <input
            type="datetime-local"
            value={form.end?.slice(0, 16) || ""}
            onChange={(e) => setForm({ ...form, end: e.target.value + ":00" })}
            className="border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>
        <input
          placeholder="Location (optional)"
          value={form.location}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
          className="w-full border rounded-lg px-3 py-2 text-sm"
        />
        <textarea
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="w-full border rounded-lg px-3 py-2 text-sm"
          rows={2}
        />
        <div className="flex gap-2">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-700"
          >
            {editingId ? "Update" : "Create"}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={() => {
                setEditingId(null);
                setForm(empty);
              }}
              className="text-sm text-gray-500 hover:underline"
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {/* Event list */}
      {loading ? (
        <p className="text-gray-500">Loading events...</p>
      ) : events.length === 0 ? (
        <p className="text-gray-500">No upcoming events.</p>
      ) : (
        <div className="bg-white rounded-xl border divide-y">
          {events.map((ev) => (
            <div key={ev.id} className="px-4 py-3 flex items-start gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-medium">{ev.summary}</p>
                <p className="text-xs text-gray-500">
                  {new Date(ev.start).toLocaleString()} &ndash;{" "}
                  {new Date(ev.end).toLocaleString()}
                </p>
                {ev.location && (
                  <p className="text-xs text-gray-400">{ev.location}</p>
                )}
              </div>
              <button
                onClick={() => handleEdit(ev)}
                className="text-xs text-gray-500 hover:text-blue-600"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(ev.id)}
                className="text-xs text-gray-500 hover:text-red-600"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
