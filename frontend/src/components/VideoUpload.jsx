import { useState } from 'react';
import { uploadVideo } from '../api';

export default function VideoUpload() {
  const [status, setStatus] = useState(null);
  const [uploading, setUploading] = useState(false);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setStatus(null);
    try {
      const result = await uploadVideo(file);
      setStatus({
        ok: true,
        message: result.message || 'Upload started successfully',
        id: result.id,
      });
    } catch (err) {
      setStatus({ ok: false, message: err.message });
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="rounded-xl bg-white shadow border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
        Upload Video for Analysis
      </h3>
      <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:border-blue-400 transition-colors">
        <svg
          className="w-8 h-8 text-gray-400 mb-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span className="text-sm text-gray-500">
          {uploading ? 'Uploading…' : 'Click to select MP4 / AVI file'}
        </span>
        <input
          type="file"
          accept="video/*"
          className="hidden"
          onChange={handleUpload}
          disabled={uploading}
        />
      </label>
      {status && (
        <div
          className={`mt-3 text-sm rounded-lg px-4 py-2 ${
            status.ok
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {status.message}
        </div>
      )}
    </div>
  );
}
