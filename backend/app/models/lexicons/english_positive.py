"""English positive sentiment lexicon.

Used by the XLM-R fallback path and shared with other models that need
an English positive lexicon. Words are stored in lowercase so that simple
whitespace tokenization matches reliably.
"""

POSITIVE_WORDS_EN: set[str] = {
    # --- Core adjectives ---
    "excellent", "great", "good", "happy", "love", "like", "amazing",
    "useful", "positive", "best", "thanks", "nice", "perfect",
    "wonderful", "fantastic", "fabulous", "marvelous", "superb",
    "brilliant", "outstanding", "exceptional", "remarkable",
    "impressive", "stunning", "gorgeous", "beautiful", "lovely",
    "delightful", "charming", "pleasant", "enjoyable", "pleasing",
    "awesome", "terrific", "tremendous", "tremendously", "magnificent",
    "glorious", "splendid", "super", "superb", "fine", "grand",

    # --- Emotions & feelings ---
    "happy", "happiness", "joy", "joyful", "joyous", "delighted",
    "glad", "pleased", "cheerful", "cheery", "merry", "jolly",
    "content", "contented", "satisfied", "satisfaction", "gratified",
    "thrilled", "ecstatic", "elated", "euphoric", "blissful",
    "bliss", "euphoria", "excited", "excitement", "enthusiastic",
    "eager", "keen", "passionate", "passion", "affectionate",
    "affection", "adore", "adored", "adoring", "fond", "fondly",
    "smitten", "enchanted", "captivated", "fascinated", "intrigued",
    "grateful", "gratitude", "thankful", "appreciative", "appreciate",
    "appreciated", "blessed", "fortunate", "lucky", "blessing",
    "hopeful", "optimistic", "optimism", "inspired", "inspiring",
    "motivated", "encouraged", "encouraging", "uplifted", "uplifting",

    # --- Praise & compliments ---
    "bravo", "kudos", "commend", "commended", "commendable",
    "praise", "praised", "praiseworthy", "applaud", "applauded",
    "applause", "acclaim", "acclaimed", " accolade", " accolades",
    "compliment", "complimented", "flatter", "flattered",
    "congratulate", "congratulations", "congrats", "well-done",
    "welldone", "kudos", "respect", "respected", "admirable", "admire",
    "admired", "admiration", "tribute", "honor", "honored", "honour",
    "honoured", "glory", "glorious", "prestigious", "esteemed",

    # --- Quality & excellence ---
    "quality", "high-quality", "top-notch", "topnotch", "first-class",
    "firstclass", "world-class", "worldclass", "premium", "superior",
    "exquisite", "elegant", "refined", "sophisticated", "polished",
    "flawless", "impeccable", "pristine", "mint", "immaculate",
    "spotless", "unblemished", "perfect", "perfection", "ideal",
    "optimal", "optimum", "stellar", "phenomenal", "phenomenally",
    "masterful", "masterpiece", "masterly", "expert", "expertly",
    "proficient", "skillful", "skilful", "adept", "capable",
    "competent", "efficient", "effective", "productive", "fruitful",
    "innovative", "innovative", "creative", "ingenious", "inventive",
    "original", "novel", "fresh", "refreshing", "imaginative",

    # --- Success & achievement ---
    "success", "successful", "succeeded", "succeed", "win", "wins",
    "winning", "won", "victory", "triumph", "triumphant", "triumphed",
    "achieve", "achieved", "achievement", "achievements", "accomplish",
    "accomplished", "accomplishment", "attain", "attained", "attainment",
    "fulfill", "fulfilled", "fulfillment", "complete", "completed",
    "completion", "finish", "finished", "master", "mastered",
    "conquer", "conquered", "overcome", "progress", "progressed",
    "progression", "advance", "advanced", "advancement", "improve",
    "improved", "improvement", "enhance", "enhanced", "enhancement",
    "boost", "boosted", "elevate", "elevated", "rise", "rose",
    "risen", "thrive", "thrived", "thriving", "flourish", "flourishing",
    "prosper", "prospered", "prosperous", "prosperity", "boom", "booming",
    "profit", "profitable", "gain", "gained", "benefit", "beneficial",
    "reward", "rewarding", "rewarded", "lucrative", "fruitful",

    # --- Value & usefulness ---
    "useful", "helpful", "beneficial", "valuable", "invaluable",
    "worthwhile", "worthy", "worth", "worthy", "treasure", "treasured",
    "precious", "priceless", "irreplaceable", "indispensable",
    "essential", "vital", "crucial", "important", "significant",
    "meaningful", "impactful", "impact", "resourceful", "practical",
    "handy", "convenient", "convenience", "accessible", "available",
    "reliable", "dependable", "trustworthy", "trusted", "secure",
    "safe", "safety", "guaranteed", "assured", "proven", "tested",
    "durable", "lasting", "enduring", "sturdy", "robust", "solid",
    "stable", "steadfast", "consistent", "coherent", "cohesive",

    # --- Beauty & aesthetics ---
    "beautiful", "beauty", "gorgeous", "stunning", "breathtaking",
    "captivating", "mesmerizing", "enchanting", "alluring", "appealing",
    "attractive", "handsome", "pretty", "cute", "adorable", "lovely",
    "elegant", "graceful", "grace", "refined", "tasteful", "stylish",
    "chic", "classy", "sophisticated", "artistic", "artful", "aesthetic",
    "picturesque", "scenic", "panoramic", "majestic", "magnificent",
    "splendid", "resplendent", "radiant", "luminous", "glowing", "shining",
    "vibrant", "vivid", "colorful", "harmonious", "symmetrical",
    "balanced", "well-proportioned", "shapely", "comely", "fair",

    # --- Strength & reliability ---
    "strong", "strength", "powerful", "mighty", "robust", "sturdy",
    "tough", "resilient", "durable", "solid", "firm", "stable",
    "steadfast", "unwavering", "unshakable", "resolute", "determined",
    "committed", "dedicated", "devoted", "loyal", "faithful", "true",
    "honest", "honesty", "sincere", "sincerity", "genuine", "authentic",
    "real", "true", "legitimate", "valid", "sound", "wholesome",
    "reliable", "dependable", "consistent", "trustworthy", "credible",
    "reputable", "respected", "esteemed", "honored", "honoured",

    # --- Recommendations & approval ---
    "recommend", "recommended", "recommendation", "suggest", "suggested",
    "advice", "advise", "advised", "endorse", "endorsed", "endorsement",
    "approve", "approved", "approval", "favor", "favored", "favorite",
    "favourite", "preferred", "prefer", "like", "liked", "likes",
    "love", "loved", "loves", "adore", "adored", "enjoy", "enjoyed",
    "enjoys", "appreciate", "appreciated", "value", "valued", "welcome",
    "welcomed", "accept", "accepted", "agree", "agreed", "support",
    "supported", "backing", "champion", "championed", "advocate",

    # --- Common positive expressions ---
    "good", "great", "nice", "cool", "sweet", "kind", "kindly",
    "gentle", "generous", "charitable", "benevolent", "compassionate",
    "caring", "warm", "friendly", "amiable", "amicable", "cordial",
    "hospitable", "welcoming", "gracious", "courteous", "polite",
    "respectful", "considerate", "thoughtful", "mindful", "attentive",
    "supportive", "encouraging", "inspiring", "motivating", "uplifting",
    "empowering", "nurturing", "mentoring", "guiding", "helpful",
    "obliging", "accommodating", "cooperative", "collaborative",
    "sympathetic", "empathetic", "understanding", "patient", "tolerant",
    "forgiving", "merciful", "gracious", "humble", "modest", "unassuming",

    # --- Dialectal / colloquial positive forms ---
    "lit", "fire", "dope", "sick", "rad", "radical", "epic",
    "legendary", "mythical", "godlike", "insane", "crazy", "wild",
    "killer", "smashing", "bangin", "banging", "boomin", "booming",
    "fly", "fresh", "clean", "crisp", "sharp", "slick", "smooth",
    "golden", "platinum", "diamond", "champion", "hero", "legend",
    "icon", "iconic", "classic", "timeless", "vintage", "retro",
    "nostalgic", "fond", "fondly", "yay", "woohoo", "yippee", "hurray",
    "hurrah", "bravo", "encore", "cheers", "hallelujah", "amen",
    "bingo", "jackpot", "eureka", "voila", "presto", "ta-da", "tada",
}
