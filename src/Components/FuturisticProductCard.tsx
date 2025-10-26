'use client';

import React, { useRef, useState } from 'react';
import {
  motion,
  useMotionTemplate,
  useMotionValue,
  useSpring,
  useTransform,
  MotionStyle,
  SpringOptions,
} from 'framer-motion';
import {
  Star,
  ShoppingCart,
  Heart,
  Eye,
  Package,
  Clock,
  CheckCircle,
  Check,
} from 'lucide-react';

type TiltProps = {
  children: React.ReactNode;
  className?: string;
  style?: MotionStyle;
  rotationFactor?: number;
  isRevese?: boolean;
  springOptions?: SpringOptions;
};

function Tilt({
  children,
  className,
  style,
  rotationFactor = 15,
  isRevese = false,
  springOptions,
}: TiltProps) {
  const ref = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const xSpring = useSpring(x, springOptions);
  const ySpring = useSpring(y, springOptions);

  const rotateX = useTransform(
    ySpring,
    [-0.5, 0.5],
    isRevese ? [rotationFactor, -rotationFactor] : [-rotationFactor, rotationFactor]
  );
  const rotateY = useTransform(
    xSpring,
    [-0.5, 0.5],
    isRevese ? [-rotationFactor, rotationFactor] : [rotationFactor, -rotationFactor]
  );

  const transform = useMotionTemplate`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const xPos = (e.clientX - rect.left) / rect.width - 0.5;
    const yPos = (e.clientY - rect.top) / rect.height - 0.5;

    x.set(xPos);
    y.set(yPos);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      className={className}
      style={{ transformStyle: 'preserve-3d', ...style, transform }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </motion.div>
  );
}

type ProductCard = {
  id: string;
  name: string;
  description: string;
  price: string;
  features: string[];
  imageUrl: string;
  badge?: string;
  rating?: number;
  reviewsCount?: number;
  availability: 'in stock' | 'out of stock' | 'pre-order';
  comparisonTags: string[];
};

interface FuturisticProductCardProps {
  product?: ProductCard;
  className?: string;
  isSelected?: boolean;
  onSelect?: (selected: boolean) => void;
}

const FuturisticProductCard = ({
  product = {
    id: '1',
    name: '',
    description:
      'Next-generation brain-computer interface with quantum processing capabilities and real-time neural mapping.',
    price: '$2,999',
    features: ['Quantum Processing', 'Neural Mapping', 'Real-time Sync', 'AI Integration'],
    imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=300&fit=crop',
    badge: 'Best Value',
    rating: 4.8,
    reviewsCount: 1247,
    availability: 'in stock',
    comparisonTags: ['Fast', 'Secure', 'Advanced'],
  },
  
  
  className = '',
  isSelected: isSelectedProp = false,
  onSelect,
  
}:



FuturisticProductCardProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [glowPosition, setGlowPosition] = useState({ x: 0, y: 0 });
  const [isSelected, setIsSelected] = useState(isSelectedProp);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setGlowPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  const toggleSelection = () => {
    const newSelected = !isSelected;
    setIsSelected(newSelected);
    onSelect?.(newSelected);
  };

  const getAvailabilityIcon = () => {
    switch (product.availability) {
      case 'in stock':
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case 'pre-order':
        return <Clock className="w-4 h-4 text-amber-400" />;
      default:
        return <Package className="w-4 h-4 text-red-400" />;
    }
  };



  const getAvailabilityColor = () => {
    switch (product.availability) {
      case 'in stock':
        return 'text-emerald-400';
      case 'pre-order':
        return 'text-amber-400';
      default:
        return 'text-red-400';
    }
  };

  return (
    <Tilt
      rotationFactor={8}
      isRevese
      springOptions={{ stiffness: 26.7, damping: 4.1, mass: 0.2 }}
      className={`group  mx-auto ${className}`}
      style={{
      width: "362px",   // 👈 your custom width
      height: "420px",  // 👈 your custom height
      fontSize: "0.9rem",
}}
    >
      <motion.div
        className="relative w-full h-full overflow-hidden rounded-2xl bg-black border border-gray-800 flex flex-col"
        style={{
          background: 'linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%)',
          boxShadow:
            '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.05)',
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onMouseMove={handleMouseMove}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Glow */}
        <motion.div
          className="absolute pointer-events-none z-10 h-40 w-40 rounded-full blur-3xl"
          style={{
            background: `radial-gradient(circle, rgba(99, 102, 241, 0.4) 0%, rgba(168, 85, 247, 0.2) 50%, rgba(0,0,0,0) 70%)`,
            left: `${glowPosition.x - 80}px`,
            top: `${glowPosition.y - 80}px`,
          }}
          animate={{
            opacity: isHovered ? 0.8 : 0,
            scale: isHovered ? 1.5 : 1,
          }}
          transition={{ duration: 0.3 }}
        />

        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `
                linear-gradient(90deg, rgba(99, 102, 241, 0.3) 1px, transparent 1px),
                linear-gradient(rgba(99, 102, 241, 0.3) 1px, transparent 1px),
                radial-gradient(circle at 20% 80%, rgba(168, 85, 247, 0.3) 1px, transparent 1px),
                radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.3) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px, 20px 20px, 40px 40px, 40px 40px',
            }}
          />
        </div>

        {/* Select Button */}
        <motion.button
          className="absolute top-4 left-4 z-20 p-2 rounded-full bg-black/50 backdrop-blur-sm border border-gray-700 text-gray-300 hover:text-green-400 transition-colors"
          onClick={toggleSelection}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Check className={`w-4 h-4 ${isSelected ? 'fill-green-400 text-green-400' : ''}`} />
        </motion.button>

        {/* Badge */}
        {product.badge && (
          <motion.div
            className="absolute top-4 left-14 z-20"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg">
              {product.badge}
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="absolute top-4 right-4 z-20 flex flex-col gap-2">
          <motion.button
            className="p-2 rounded-full bg-black/50 backdrop-blur-sm border border-gray-700 text-gray-300 hover:text-red-400 transition-colors"
            onClick={() => setIsLiked(!isLiked)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <Heart className={`w-4 h-4 ${isLiked ? 'fill-red-400 text-red-400' : ''}`} />
          </motion.button>
          <motion.button
            className="p-2 rounded-full bg-black/50 backdrop-blur-sm border border-gray-700 text-gray-300 hover:text-blue-400 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <Eye className="w-4 h-4" />
          </motion.button>
        </div>

        {/* Product Image */}
        <div className="relative h-48 overflow-hidden">
          <motion.img
            src={product.imageUrl}
            alt={product.name}
            className="w-full h-full object-cover"
            style={{
              filter: isHovered ? 'brightness(1.1) contrast(1.1)' : 'brightness(0.9) contrast(0.9)',
            }}
            transition={{ duration: 0.3 }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        </div>

        {/* Content Section */}
        <div className="relative p-4 z-20 flex-grow flex flex-col gap-2"style={{ marginLeft: '6px'  }}>
        {product.rating && (
        <div className="flex items-center gap-2 mb-3">
        <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < Math.floor(product.rating!) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-400">
                {product.rating} ({product.reviewsCount})
              </span>
            </div>
          )}

          <motion.h3
            className="text-xl font-bold text-white mb-2 leading-tight"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {product.name}
          </motion.h3>

          <motion.p
            className="text-gray-400 text-sm mb-4 line-clamp-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {product.description}
          </motion.p>

          <div className="mb-4 flex flex-wrap gap-1">
            {product.features.slice(0, 3).map((feature, index) => (
              <motion.span
                key={feature}
                className="px-2 py-1 text-xs rounded-md bg-gray-800 text-gray-300 border border-gray-700"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
              >
                {feature}
              </motion.span>
            ))}
            {product.features.length > 3 && (
              <span className="px-2 py-1 text-xs rounded-md bg-gray-800 text-gray-300 border border-gray-700">
                +{product.features.length - 3}
              </span>
            )}
          </div>

          <div className="mb-4 flex flex-wrap gap-1">
            {product.comparisonTags.map((tag, index) => (
              <motion.span
                key={tag}
                className="px-2 py-1 text-xs rounded-full bg-gradient-to-r from-purple-600/20 to-blue-600/20 text-purple-300 border border-purple-500/30"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
              >
                {tag}
              </motion.span>
            ))}
          </div>

          <div className="flex items-center gap-2 mb-4" style={{ marginTop: '1px' }}>
            {getAvailabilityIcon()}
            <span className={`text-sm font-medium capitalize ${getAvailabilityColor()}`}>
              {product.availability}
            </span>
          </div>

          <div className="flex items-center justify-between mt-auto" style={{ marginTop: '7px' }}>
            <motion.div
              className="text-2xl font-bold text-white"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              {product.price}
            </motion.div>

            <motion.button
              className=" flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold text-sm hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              style={{ margin: '10px' }}
              
            >
              <ShoppingCart className="w-4 h-4"  />
              Add to Cart
            </motion.button>
          </div>
        </div>

        {/* Border Animation */}
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            background: `linear-gradient(90deg, transparent 0%, rgba(99, 102, 241, 0.5) 50%, transparent 100%)`,
            backgroundSize: '200% 1px',
            backgroundRepeat: 'no-repeat',
          }}
          animate={{
            backgroundPosition: isHovered ? '100% 0' : '0% 0',
          }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
        />
        
      </motion.div>
      
    </Tilt>
  );
};

export default FuturisticProductCard;
