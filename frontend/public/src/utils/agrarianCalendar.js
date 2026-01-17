/**
 * Agrarian Calendar Utility
 * Manages agricultural periods based on exact requested mapping.
 */

export const AGRARIAN_PERIODS = [
    {
        id: 'P1',
        name: 'Winter Dormancy',
        range: 'Jan 1 - Jan 20',
        start: { month: 0, day: 1 },
        end: { month: 0, day: 20 },
        description: 'Biological activity is at its minimum. Focus on soil preparation and machinery maintenance.',
        suitable: ['Fava Beans', 'Garlic', 'Winter Spinach'],
        wait: [{ name: 'Potatoes', reason: 'Soil still too cold' }],
        avoid: ['Tomatoes', 'Peppers', 'Melons'],
        warning: 'Protect sensitive seedlings from frost.',
        nextPeriod: 'P2'
    },
    {
        id: 'P2',
        name: 'Late Winter',
        range: 'Jan 21 - Feb 15',
        start: { month: 0, day: 21 },
        end: { month: 1, day: 15 },
        description: 'First signs of awakening. Days are lengthening slowly. Ideal for tuber preparation.',
        suitable: ['Potatoes', 'Onions', 'Carrots'],
        wait: [{ name: 'Artichoke', reason: 'Better in P3 stability' }],
        avoid: ['Summer Squash', 'Cucumbers'],
        warning: 'Watch for sudden cold snaps.',
        nextPeriod: 'P3'
    },
    {
        id: 'P3',
        name: 'Early Spring',
        range: 'Feb 16 - Mar 14',
        start: { month: 1, day: 16 },
        end: { month: 2, day: 14 },
        description: 'Optimal window for early spring planting as soil temperature rises.',
        suitable: ['Lettuce', 'Spinach', 'Peas', 'Artichoke'],
        wait: [{ name: 'Tomatoes', reason: 'Start in nursery first' }],
        avoid: ['Watermelon', 'Okra'],
        warning: 'Ensure good drainage for spring rains.',
        nextPeriod: 'P4'
    },
    {
        id: 'P4',
        name: 'Spring Stability',
        range: 'Mar 15 - Apr 30',
        start: { month: 2, day: 15 },
        end: { month: 3, day: 30 },
        description: 'The most productive planting window of the year. Stable temperatures and moisture.',
        suitable: ['Tomatoes', 'Peppers', 'Eggplant', 'Cucumbers'],
        wait: [{ name: 'Late Melons', reason: 'Wait for hot ground' }],
        avoid: ['Cold-weather Spinach', 'Late Garlic'],
        warning: 'Frost risk is low, but wind can be high.',
        nextPeriod: 'P5'
    },
    {
        id: 'P5',
        name: 'Summer Stress',
        range: 'May 1 - Jun 15',
        start: { month: 4, day: 1 },
        end: { month: 5, day: 15 },
        description: 'Temperatures rise quickly. Priority shifts to irrigation and mulch.',
        suitable: ['Okra', 'Melons', 'Hot Peppers'],
        wait: [{ name: 'Autumn Spud', reason: 'Soil too hot to plant now' }],
        avoid: ['Lettuce', 'Cabbage'],
        warning: 'Irrigate early morning or late evening.',
        nextPeriod: 'P6'
    },
    {
        id: 'P6',
        name: 'Peak Summer Risk',
        range: 'Jun 16 - Aug 31',
        start: { month: 5, day: 16 },
        end: { month: 7, day: 31 },
        description: 'Maximum heat and dry winds (Sirocco). Focus on crop survival and harvesting.',
        suitable: ['Olives', 'Citrus', 'Mature Melons'],
        wait: [{ name: 'Winter Greens', reason: 'Wait for heat break in Sep' }],
        avoid: ['All leaf vegetables', 'Newly planted trees'],
        warning: 'Extreme sunscald risk for fruit.',
        nextPeriod: 'P7'
    },
    {
        id: 'P7',
        name: 'Autumn Recovery',
        range: 'Sep 1 - Oct 15',
        start: { month: 8, day: 1 },
        end: { month: 9, day: 15 },
        description: 'First refreshing rains. Excellent for cool-season vegetables.',
        suitable: ['Cabbage', 'Cauliflower', 'Broccoli', 'Swiss Chard'],
        wait: [{ name: 'Wheat', reason: 'Wait for deeper moisture' }],
        avoid: ['Summer crops', 'Late Tomatoes'],
        warning: 'High humidity may lead to fungal issues.',
        nextPeriod: 'P8'
    },
    {
        id: 'P8',
        name: 'Pre-Winter',
        range: 'Oct 16 - Nov 30',
        start: { month: 9, day: 16 },
        end: { month: 10, day: 30 },
        description: 'Main window for cereal planting and late-year harvesting.',
        suitable: ['Wheat', 'Barley', 'Broad Beans', 'Lentils'],
        wait: [{ name: 'Next year seeds', reason: 'Collect and store' }],
        avoid: ['Heat lovers', 'Zucchini'],
        warning: 'Clear all drainage lines before winter.',
        nextPeriod: 'P9'
    },
    {
        id: 'P9',
        name: 'Early Cold Season',
        range: 'Dec 1 - Dec 31',
        start: { month: 11, day: 1 },
        end: { month: 11, day: 31 },
        description: 'Entering dormancy. Harvesting of citrus and olives continues.',
        suitable: ['Citrus', 'Olives', 'Wheat (late)', 'Oats'],
        wait: [{ name: 'Spring prep', reason: 'Analyze soil' }],
        avoid: ['Summer Veg', 'Peppers'],
        warning: 'Monitor for early frost damage.',
        nextPeriod: 'P1'
    }
];

export const getCurrentPeriod = (date = new Date()) => {
    const month = date.getMonth();
    const day = date.getDate();

    for (const period of AGRARIAN_PERIODS) {
        if ((month === period.start.month && day >= period.start.day) || (month > period.start.month)) {
            if ((month === period.end.month && day <= period.end.day) || (month < period.end.month)) {
                // Add backward compatibility aliases
                return {
                    ...period,
                    recommended: period.suitable,
                    characteristics: [period.description],
                    bestCrops: period.suitable
                };
            }
        }
    }
    // Handle Dec 31st/Special cases
    const fallback = AGRARIAN_PERIODS[8];
    return {
        ...fallback,
        recommended: fallback.suitable,
        characteristics: [fallback.description],
        bestCrops: fallback.suitable
    };
};

export const getNextPeriod = (currentPeriod) => {
    if (!currentPeriod || !currentPeriod.nextPeriod) return AGRARIAN_PERIODS[0];
    const next = AGRARIAN_PERIODS.find(p => p.id === currentPeriod.nextPeriod);
    return next || AGRARIAN_PERIODS[0];
};

export const getDaysUntilNextPeriod = (nextPeriod, currentDate = new Date()) => {
    const currentYear = currentDate.getFullYear();
    let nextPeriodStart = new Date(currentYear, nextPeriod.start.month, nextPeriod.start.day);
    if (nextPeriodStart < currentDate) {
        nextPeriodStart.setFullYear(currentYear + 1);
    }
    const diffTime = nextPeriodStart - currentDate;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const getPeriodPerformance = (userId) => {
    // Simulated historical data
    return {
        successRate: 85,
        rating: 'Excellent!',
        status: 'good'
    };
};
