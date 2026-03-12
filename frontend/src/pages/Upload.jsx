import { useState, useEffect, useRef, useMemo } from 'react';
import { CloudUpload, Loader, CheckCircle, XCircle, Info, X } from 'lucide-react';
import { uploadVideo, fetchUploadStatus } from '../api';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadPct, setUploadPct] = useState(0); // 0-100 upload transfer %
  const [job, setJob] = useState(null); // { id, status, progress, log }
  const pollRef = useRef(null);

  // Create a blob URL for video preview, revoke on cleanup
  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl); }, [previewUrl]);

  function handleFileChange(e) {
    setFile(e.target.files[0] || null);
    setJob(null);
    setUploadPct(0);
  }

  function clearFile() {
    setFile(null);
    setJob(null);
    setUploadPct(0);
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setUploadPct(0);
    setJob(null);
    try {
      const result = await uploadVideo(file, (pct) => setUploadPct(pct));
      setJob({ id: result.id, status: result.status, progress: 0, log: result.message || '' });
    } catch (err) {
      setJob({ id: null, status: 'FAILED', progress: 0, log: err.message });
    } finally {
      setUploading(false);
    }
  }

  // Poll for status updates while processing
  useEffect(() => {
    if (!job?.id || job.status === 'COMPLETED' || job.status === 'FAILED') {
      clearInterval(pollRef.current);
      return;
    }
    pollRef.current = setInterval(async () => {
      try {
        const d = await fetchUploadStatus(job.id);
        setJob((prev) => ({ ...prev, status: d.status, progress: d.progress ?? 0, log: d.log }));
        if (d.status === 'COMPLETED' || d.status === 'FAILED') {
          clearInterval(pollRef.current);
        }
      } catch {
        /* ignore */
      }
    }, 1500);
    return () => clearInterval(pollRef.current);
  }, [job?.id, job?.status]);

  // Derive display percentage
  const displayPct = uploading
    ? uploadPct
    : job?.status === 'COMPLETED'
      ? 100
      : job?.progress ?? 0;

  const STATUS_CONFIG = {
    PENDING:    { color: 'text-yellow-600 bg-yellow-50 border-yellow-200', barColor: 'bg-yellow-500' },
    PROCESSING: { color: 'text-blue-600 bg-blue-50 border-blue-200', barColor: 'bg-blue-500' },
    COMPLETED:  { color: 'text-green-600 bg-green-50 border-green-200', barColor: 'bg-green-500' },
    FAILED:     { color: 'text-red-600 bg-red-50 border-red-200', barColor: 'bg-red-500' },
  };

  const statusCfg = uploading
    ? { color: 'text-blue-600 bg-blue-50 border-blue-200', barColor: 'bg-blue-500' }
    : job
      ? STATUS_CONFIG[job.status] || STATUS_CONFIG.PENDING
      : null;

  const showStatus = uploading || job;

  // Status label text
  const statusLabel = uploading
    ? 'Uploading'
    : job?.status === 'PENDING'
      ? 'Queued'
      : job?.status === 'PROCESSING'
        ? 'Processing'
        : job?.status === 'COMPLETED'
          ? 'Completed'
          : job?.status === 'FAILED'
            ? 'Failed'
            : '';

  const StatusIcon = uploading
    ? Loader
    : job?.status === 'COMPLETED'
      ? CheckCircle
      : job?.status === 'FAILED'
        ? XCircle
        : Loader;

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900">Upload Video for Analysis</h2>

      {/* Upload card */}
      <div className="rounded-xl bg-white shadow border border-gray-200 p-6">
        {!file ? (
          /* Drop zone */
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-10 cursor-pointer hover:border-blue-400 transition-colors">
            <CloudUpload className="w-10 h-10 text-gray-400 mb-3" />
            <span className="text-sm text-gray-500">Click to select MP4 / AVI file</span>
            <input
              type="file"
              accept="video/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </label>
        ) : (
          /* Video preview */
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 truncate">{file.name}</span>
              <button
                onClick={clearFile}
                className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <video
              src={previewUrl}
              controls
              className="w-full rounded-lg border border-gray-200 bg-black max-h-80 object-contain"
            />
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="mt-4 w-full py-2.5 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Uploading… {uploadPct}%
            </>
          ) : (
            <>
              <CloudUpload className="w-4 h-4" />
              Upload &amp; Process
            </>
          )}
        </button>
      </div>

      {/* Progress / Status card */}
      {showStatus && statusCfg && (
        <div className={`rounded-xl border p-5 ${statusCfg.color}`}>
          {/* Header row */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold flex items-center gap-2">
              <StatusIcon className={`w-4 h-4 ${job?.status !== 'COMPLETED' && job?.status !== 'FAILED' ? 'animate-spin' : ''}`} />
              {statusLabel}
            </span>
            <span className="text-lg font-bold tabular-nums">{displayPct}%</span>
          </div>

          {/* Progress bar */}
          <div className="w-full h-2.5 rounded-full bg-white/50 overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all duration-500 ease-out ${statusCfg.barColor}`}
              style={{ width: `${displayPct}%` }}
            />
          </div>

          {/* Log text */}
          {job?.log && (
            <p className="text-xs mt-2 whitespace-pre-wrap opacity-80">{job.log}</p>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="rounded-xl bg-gray-100 border border-gray-200 p-5 text-sm text-gray-500 space-y-1">
        <p className="font-medium text-gray-700 flex items-center gap-2">
          <Info className="w-4 h-4" />
          How it works
        </p>
        <ol className="list-decimal list-inside space-y-0.5">
          <li>Select a traffic video file (MP4, AVI)</li>
          <li>Video is uploaded and queued for processing</li>
          <li>YOLOv8 + BoT-SORT detects &amp; tracks each unique vehicle</li>
          <li>Results stream to the dashboard in real time via WebSocket</li>
        </ol>
      </div>
    </div>
  );
}
