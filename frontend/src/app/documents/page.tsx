"use client";

import { useState } from "react";
import { parseDocument } from "@/lib/api";

type Element = {
  type: string;
  text: string;
  metadata?: Record<string, any>;
};

export default function DocumentsPage() {
  const [elements, setElements] = useState<Element[]>([]);
  const [filename, setFilename] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleParse = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError("");
    setElements([]);
    setFilename(file.name);

    const formData = new FormData();
    formData.append("file", file);
    try {
      const data = await parseDocument(formData);
      setElements(data.elements);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Document Parser</h1>
      <p className="text-gray-600 text-sm">
        Upload a PDF, DOCX, PPTX, or other document to parse it with Unstructured.
      </p>

      <label className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg text-sm cursor-pointer hover:bg-blue-700">
        Choose Document
        <input type="file" className="hidden" onChange={handleParse} />
      </label>

      {loading && <p className="text-gray-500">Parsing {filename}...</p>}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {elements.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold">
            {filename} &mdash; {elements.length} elements
          </h2>
          <div className="bg-white rounded-xl border divide-y max-h-[600px] overflow-y-auto">
            {elements.map((el, i) => (
              <div key={i} className="px-4 py-3">
                <span className="inline-block bg-gray-100 text-gray-600 text-xs rounded px-2 py-0.5 mb-1">
                  {el.type}
                </span>
                <p className="text-sm whitespace-pre-wrap">{el.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
