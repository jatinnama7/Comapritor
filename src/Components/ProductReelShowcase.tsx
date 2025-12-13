"use client";

import React, { useState } from "react";
import { motion, useInView } from "framer-motion";
import { Card, CardContent, CardFooter } from "@/Components/ui/card";
import { Button } from "@/Components/ui/button";
import { Badge } from "@/Components/ui/badge";
import {
  Heart,
  ShoppingCart,
  Star,
  Play,
  Volume2,
  VolumeX,
} from "lucide-react";
import { cn } from "@/lib/Utils";

interface ProductReelCardProps {
  id: string;
  videoSrc: string;
  thumbnailSrc: string;
  title: string;
  price: number;
  originalPrice?: number;
  rating?: number;
  reviewCount?: number;
  aspectRatio: "9/16" | "4/5" | "1/1" | "16/9";
  isNew?: boolean;
  discount?: number;
}

const ProductReelCard = ({
  videoSrc,
  thumbnailSrc,
  title,
  price,
  originalPrice,
  rating = 4.5,
  reviewCount = 0,
  aspectRatio,
  isNew = false,
  discount = 0,
}: ProductReelCardProps) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const videoRef = React.useRef<HTMLVideoElement>(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  return (
    <Card className="overflow-hidden group bg-background text-foreground shadow-lg hover:shadow-xl transition-all duration-300 rounded-lg">
      <div
        className="relative overflow-hidden cursor-pointer"
        style={{ aspectRatio }}
        onClick={togglePlay}
      >
        <video
          ref={videoRef}
          src={videoSrc}
          poster={thumbnailSrc}
          className="w-full h-full object-cover"
          loop
          muted={isMuted}
          playsInline
        />

        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
              <Play className="h-8 w-8 text-black ml-1" fill="black" />
            </div>
          </div>
        )}

        <div className="absolute top-3 left-3 flex flex-col gap-2">
          {isNew && (
            <Badge className="bg-blue-500 hover:bg-blue-500/90">New</Badge>
          )}
          {discount > 0 && (
            <Badge className="bg-rose-500 hover:bg-rose-500/90">
              -{discount}%
            </Badge>
          )}
        </div>

        <div className="absolute top-3 right-3 flex flex-col gap-2">
          <Button
            variant="secondary"
            size="icon"
            className={`h-8 w-8 rounded-full bg-background/80 backdrop-blur-sm shadow-sm ${
              isWishlisted ? "text-rose-500" : ""
            }`}
            onClick={(e) => {
              e.stopPropagation();
              setIsWishlisted(!isWishlisted);
            }}
          >
            <Heart
              className={`h-4 w-4 ${isWishlisted ? "fill-rose-500" : ""}`}
            />
          </Button>
          {isPlaying && (
            <Button
              variant="secondary"
              size="icon"
              className="h-8 w-8 rounded-full bg-background/80 backdrop-blur-sm shadow-sm"
              onClick={toggleMute}
            >
              {isMuted ? (
                <VolumeX className="h-4 w-4" />
              ) : (
                <Volume2 className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      <CardContent className="p-4">
        <div className="space-y-2">
          <h3 className="font-medium line-clamp-2 text-sm">{title}</h3>
          <div className="flex items-center gap-2">
            <div className="flex items-center">
              <Star className="h-3 w-3 fill-amber-500 text-amber-500" />
              <span className="ml-1 text-xs font-medium">{rating}</span>
            </div>
            {reviewCount > 0 && (
              <span className="text-xs text-muted-foreground">
                ({reviewCount})
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-semibold">${price.toFixed(2)}</span>
            {originalPrice && originalPrice > price && (
              <span className="text-sm text-muted-foreground line-through">
                ${originalPrice.toFixed(2)}
              </span>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0">
        <Button className="w-full" size="sm">
          <ShoppingCart className="mr-2 h-4 w-4" />
          Add to Cart
        </Button>
      </CardFooter>
    </Card>
  );
};

const ProductReelMasonry = ({
  products,
}: {
  products: ProductReelCardProps[];
}) => {
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    },
  };

  return (
    <motion.div
      ref={ref}
      className="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-4 space-y-4 p-4"
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={containerVariants}
    >
      {products.map((product) => (
        <motion.div
          key={product.id}
          className="break-inside-avoid mb-4"
          variants={itemVariants}
        >
          <ProductReelCard {...product} />
        </motion.div>
      ))}
    </motion.div>
  );
};

export default function ProductReelShowcase() {
  const sampleProducts: ProductReelCardProps[] = [
    {
      id: "1",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
      title: "Premium Wireless Headphones",
      price: 199.99,
      originalPrice: 299.99,
      rating: 4.8,
      reviewCount: 234,
      aspectRatio: "9/16",
      isNew: true,
      discount: 33,
    },
    {
      id: "2",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
      title: "Smart Watch Series 5",
      price: 349.99,
      originalPrice: 449.99,
      rating: 4.6,
      reviewCount: 189,
      aspectRatio: "1/1",
      discount: 22,
    },
    {
      id: "3",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1572635196237-14b3f281503f",
      title: "Designer Sunglasses",
      price: 129.99,
      rating: 4.9,
      reviewCount: 456,
      aspectRatio: "4/5",
      isNew: true,
    },
    {
      id: "4",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1491553895911-0055eca6402d",
      title: "Leather Sneakers",
      price: 89.99,
      originalPrice: 129.99,
      rating: 4.7,
      reviewCount: 312,
      aspectRatio: "16/9",
      discount: 31,
    },
    {
      id: "5",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
      title: "Minimalist Backpack",
      price: 79.99,
      rating: 4.5,
      reviewCount: 178,
      aspectRatio: "9/16",
    },
    {
      id: "6",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1434389677669-e08b4cac3105",
      title: "Vintage Camera",
      price: 599.99,
      originalPrice: 799.99,
      rating: 4.9,
      reviewCount: 89,
      aspectRatio: "4/5",
      isNew: true,
      discount: 25,
    },
    {
      id: "7",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1560343090-f0409e92791a",
      title: "Ceramic Coffee Mug Set",
      price: 39.99,
      rating: 4.6,
      reviewCount: 523,
      aspectRatio: "1/1",
    },
    {
      id: "8",
      videoSrc: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
      thumbnailSrc: "https://images.unsplash.com/photo-1585386959984-a4155224a1ad",
      title: "Wool Blend Coat",
      price: 249.99,
      originalPrice: 349.99,
      rating: 4.8,
      reviewCount: 267,
      aspectRatio: "9/16",
      discount: 29,
    },
  ];

  return (
    <div className="min-h-screen bg-black py-12 ">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Shopping Reels
          </h1>
          <p className="text-lg text-gray-400">
            Discover products through engaging video content
          </p>
        </div>
        <ProductReelMasonry products={sampleProducts} />
      </div>
    </div>
  );
}
