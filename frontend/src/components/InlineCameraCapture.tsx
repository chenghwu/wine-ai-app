'use client'

import { useRef, useState, useEffect } from 'react'
import { Camera, Upload, RotateCcw, X, Check } from 'lucide-react'

interface InlineCameraCaptureProps {
  isVisible: boolean
  onClose: () => void
  onImageCapture: (imageData: string, file?: File) => void
}

export function InlineCameraCapture({ isVisible, onClose, onImageCapture }: InlineCameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment')

  // Initialize camera when component becomes visible
  useEffect(() => {
    if (isVisible && !capturedImage) {
      startCamera()
    } else if (!isVisible) {
      stopCamera()
      setCapturedImage(null)
      setCameraError(null)
    }

    return () => {
      stopCamera()
    }
  }, [isVisible, facingMode, capturedImage])

  const startCamera = async () => {
    try {
      setCameraError(null)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      })
      
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      setCameraError('Unable to access camera. Please check permissions or use gallery upload.')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')

      if (ctx) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        ctx.drawImage(video, 0, 0)
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8)
        setCapturedImage(imageData)
        stopCamera()
      }
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        setCapturedImage(result)
        stopCamera()
      }
      reader.readAsDataURL(file)
    }
  }

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user')
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    startCamera()
  }

  const confirmImage = () => {
    if (capturedImage) {
      onImageCapture(capturedImage)
      onClose()
    }
  }

  if (!isVisible) return null

  return (
    <div className="w-full mt-3 bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800">
        <h3 className="text-lg font-semibold text-white">
          {capturedImage ? 'Confirm Image' : 'Capture Wine Label'}
        </h3>
        <button
          onClick={onClose}
          className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
        >
          <X size={20} className="text-zinc-400" />
        </button>
      </div>

      {/* Camera/Image Area */}
      <div className="relative bg-black aspect-[4/3] flex items-center justify-center">
        {capturedImage ? (
          // Image preview
          <img
            src={capturedImage}
            alt="Captured wine label"
            className="max-w-full max-h-full object-contain"
          />
        ) : cameraError ? (
          // Error state
          <div className="text-center text-zinc-400 p-6">
            <Camera size={48} className="mx-auto mb-4 opacity-50" />
            <p className="mb-2">{cameraError}</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-rose-400 hover:text-rose-300 underline"
            >
              Choose from gallery instead
            </button>
          </div>
        ) : (
          // Live camera feed
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
        )}

        {/* Hidden canvas for capture */}
        <canvas ref={canvasRef} className="hidden" />
        
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Controls */}
      <div className="p-4 bg-zinc-800">
        {capturedImage ? (
          // Confirmation controls
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={retakePhoto}
              className="flex items-center space-x-2 px-4 py-2 bg-zinc-600 hover:bg-zinc-700 rounded-lg text-zinc-300 transition-colors"
            >
              <RotateCcw size={16} />
              <span>Retake</span>
            </button>
            <button
              onClick={confirmImage}
              className="flex items-center space-x-2 px-6 py-2 bg-rose-800 hover:bg-rose-900 rounded-lg text-white font-semibold transition-colors"
            >
              <Check size={16} />
              <span>Use this image</span>
            </button>
          </div>
        ) : (
          // Camera controls
          <div className="flex items-center justify-between">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-lg text-zinc-300 transition-colors"
            >
              <Upload size={16} />
              <span>Gallery</span>
            </button>

            <button
              onClick={capturePhoto}
              disabled={!stream || cameraError !== null}
              className="w-16 h-16 bg-white hover:bg-gray-100 rounded-full border-4 border-zinc-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />

            <button
              onClick={switchCamera}
              disabled={!stream || cameraError !== null}
              className="flex items-center space-x-2 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-lg text-zinc-300 transition-colors disabled:opacity-50"
            >
              <RotateCcw size={16} />
              <span>Flip</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}