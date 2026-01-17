/**
 * Crop selection card component
 */
import React from 'react';
import { CheckCircle } from 'lucide-react';
import { CROP_ICONS } from '../utils/constants';

// Map crop names to background images - using high-quality, accurate images
const getCropImage = (cropName) => {
  const imageMap = {
    // Vegetables
    'Artichoke': '/images/crops/artichoke.jpg',
    'Garlic': '/images/crops/garlic.png',
    'Okra': '/images/crops/okra.png',
    'Onion': 'https://images.unsplash.com/photo-1508747703725-719777637510?w=600&h=600&fit=crop&q=80',
    'Pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=600&h=600&fit=crop&q=80',
    'Potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&h=600&fit=crop&q=80',
    'Zucchini': '/images/crops/zucchini.png',
    'Carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&h=600&fit=crop&q=80',
    'Carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&h=600&fit=crop&q=80',
    'Spinach': '/images/crops/spinach.jpg',

    // Fruits
    'Almond': '/images/crops/almond.png',
    'Citrus': '/images/crops/citrus.png',
    'Grape': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600&h=600&fit=crop&q=80',
    'Olive': '/images/crops/olives.jpg',
    'Tomato': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&h=600&fit=crop&q=80',
    'Watermelon': '/images/crops/watermelon.jpg',

    // Legumes
    'Chickpea': '/images/crops/chickpeas.png',
    'Chickpeas': '/images/crops/chickpeas.png',
    'Lentil': '/images/crops/lentils.jpg',
    'Lentils': '/images/crops/lentils.jpg',
    'Fava Bean': '/images/crops/fava_beans.jpg',
    'Fava Beans': '/images/crops/fava_beans.jpg',
    'Green Pea': '/images/crops/green_peas.jpg',
    'Green Peas': '/images/crops/green_peas.jpg',

    // Grains
    'Wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&h=600&fit=crop&q=80',
    'Melon': '/images/crops/melon.png',
  };
  return imageMap[cropName] || 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600&h=600&fit=crop&q=80';
};

const CropCard = ({ crop, selected, onClick }) => {
  const icon = crop.icon || CROP_ICONS[crop.name] || '🌱';

  const handleClick = () => {
    const cropId = parseInt(crop.id, 10);
    console.log('Crop clicked:', { crop, cropId, type: typeof cropId });
    onClick(cropId);
  };

  return (
    <button
      onClick={handleClick}
      className={`
        relative p-4 sm:p-6 rounded-2xl border-2 transition-all transform hover:scale-105 active:scale-95
        flex flex-col items-center justify-end text-center h-32 sm:h-40 w-full overflow-hidden
        ${selected
          ? 'border-emerald-500 shadow-xl scale-105 ring-4 ring-emerald-200'
          : 'border-slate-200 hover:border-emerald-300 hover:shadow-lg'
        }
      `}
      style={{
        backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.4)), url('${getCropImage(crop.name)}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
      aria-pressed={selected}
      aria-label={`Select ${crop.name}`}
    >
      <div className="relative z-10 bg-white/95 backdrop-blur-sm rounded-xl px-4 py-2 w-full min-w-[100px] flex items-center justify-center min-h-[3rem]">
        <div className="text-[10px] sm:text-xs font-black text-slate-800 text-center leading-tight w-full">
          {crop.name}
        </div>
      </div>
      {selected && (
        <div className="absolute top-1 right-1 sm:top-2 sm:right-2">
          <CheckCircle className="text-green-600 sm:w-6 sm:h-6" size={18} fill="currentColor" />
        </div>
      )}
    </button>
  );
};

export default CropCard;