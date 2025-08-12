'use client'

import { useRef, useState, useEffect } from 'react'
import { Camera, Upload, RotateCcw, X, Check } from 'lucide-react'
import Image from 'next/image'

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
          width: { ideal: 1080 },
          height: { ideal: 1440 }
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

  const handleConfirm = () => {
    if (capturedImage) {
      onImageCapture(capturedImage)
    }
  }

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4 bg-zinc-900 flex-shrink-0">
        <h3 className="text-lg font-medium text-white">
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
      <div className="relative bg-gradient-to-b from-zinc-900 via-black to-zinc-900 flex-1 flex items-center justify-center">
        <div className="w-full max-w-sm mx-4 aspect-[3/4] relative bg-black rounded-lg overflow-hidden shadow-2xl">
          {capturedImage ? (
            // Image preview
            <Image
              src={capturedImage}
              alt="Captured wine label"
              fill
              className="object-contain"
              unoptimized
            />
          ) : cameraError ? (
            // Error state
            <div className="absolute inset-0 flex items-center justify-center">
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
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-center items-center gap-6 p-4 pb-6 bg-zinc-900 flex-shrink-0 safe-area-inset-bottom">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex flex-col items-center gap-2 p-3 hover:bg-zinc-800 rounded-lg transition-colors"
        >
          <Upload size={24} className="text-zinc-400" />
          <span className="text-xs text-zinc-400">Gallery</span>
        </button>

        {capturedImage ? (
          <>
            <button
              onClick={retakePhoto}
              className="flex flex-col items-center gap-2 p-3 hover:bg-zinc-800 rounded-lg transition-colors"
            >
              <RotateCcw size={24} className="text-zinc-400" />
              <span className="text-xs text-zinc-400">Retake</span>
            </button>
            <button
              onClick={handleConfirm}
              className="bg-rose-600 hover:bg-rose-700 px-6 py-3 rounded-lg font-medium text-white transition-colors flex items-center gap-2"
            >
              <Check size={20} />
              Use This Image
            </button>
          </>
        ) : (
          <>
            <button
              onClick={capturePhoto}
              disabled={!stream}
              className="w-16 h-16 bg-white rounded-full border-4 border-zinc-300 hover:border-zinc-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />
            <button
              onClick={switchCamera}
              className="flex flex-col items-center gap-2 p-3 hover:bg-zinc-800 rounded-lg transition-colors"
            >
              <RotateCcw size={24} className="text-zinc-400" />
              <span className="text-xs text-zinc-400">Flip</span>
            </button>
          </>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  )
}