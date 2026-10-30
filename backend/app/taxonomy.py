"""Full 14-Crop & 38-Class Taxonomy and Trilingual Knowledge Base for Hassad AI."""
from typing import Dict, List, Any

#Ordered 38 classes matching efficient-classification.ipynb training_set.class_names
CLASS_NAMES_38: List[str] = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

CROP_METADATA: Dict[str, Dict[str, Any]] = {
    "Tomato": {
        "id": "crp_tomato",
        "name_en": "Tomato",
        "name_ar": "طماطم",
        "name_fr": "Tomate",
        "scientific_name": "Solanum lycopersicum",
        "icon": "🍅",
        "growth_cycle_days": 110,
        "shelf_life_days": 10,
        "mitidja_priority": True,
    },
    "Potato": {
        "id": "crp_potato",
        "name_en": "Potato",
        "name_ar": "بطاطا",
        "name_fr": "Pomme de terre",
        "scientific_name": "Solanum tuberosum",
        "icon": "🥔",
        "growth_cycle_days": 105,
        "shelf_life_days": 45,
        "mitidja_priority": True,
    },
    "Pepper, bell": {
        "id": "crp_pepper",
        "name_en": "Bell Pepper",
        "name_ar": "فلفل حلو",
        "name_fr": "Poivron",
        "scientific_name": "Capsicum annuum",
        "icon": "🫑",
        "growth_cycle_days": 95,
        "shelf_life_days": 14,
        "mitidja_priority": True,
    },
    "Orange": {
        "id": "crp_orange",
        "name_en": "Orange (Citrus)",
        "name_ar": "برتقال (حمضيات)",
        "name_fr": "Orange (Agrumes)",
        "scientific_name": "Citrus × sinensis",
        "icon": "🍊",
        "growth_cycle_days": 240,
        "shelf_life_days": 30,
        "mitidja_priority": True,
    },
    "Corn (maize)": {
        "id": "crp_corn",
        "name_en": "Corn (Maize)",
        "name_ar": "ذرة",
        "name_fr": "Maïs",
        "scientific_name": "Zea mays",
        "icon": "🌽",
        "growth_cycle_days": 120,
        "shelf_life_days": 60,
        "mitidja_priority": True,
    },
    "Apple": {
        "id": "crp_apple",
        "name_en": "Apple",
        "name_ar": "تفاح",
        "name_fr": "Pomme",
        "scientific_name": "Malus domestica",
        "icon": "🍎",
        "growth_cycle_days": 160,
        "shelf_life_days": 60,
        "mitidja_priority": True,
    },
    "Grape": {
        "id": "crp_grape",
        "name_en": "Grape",
        "name_ar": "عنب",
        "name_fr": "Raisin",
        "scientific_name": "Vitis vinifera",
        "icon": "🍇",
        "growth_cycle_days": 150,
        "shelf_life_days": 12,
        "mitidja_priority": True,
    },
    "Peach": {
        "id": "crp_peach",
        "name_en": "Peach",
        "name_ar": "خوخ",
        "name_fr": "Pêche",
        "scientific_name": "Prunus persica",
        "icon": "🍑",
        "growth_cycle_days": 135,
        "shelf_life_days": 10,
        "mitidja_priority": True,
    },
    "Strawberry": {
        "id": "crp_strawberry",
        "name_en": "Strawberry",
        "name_ar": "فراولة",
        "name_fr": "Fraise",
        "scientific_name": "Fragaria × ananassa",
        "icon": "🍓",
        "growth_cycle_days": 90,
        "shelf_life_days": 5,
        "mitidja_priority": True,
    },
    "Cherry (including sour)": {
        "id": "crp_cherry",
        "name_en": "Cherry",
        "name_ar": "كرز",
        "name_fr": "Cerise",
        "scientific_name": "Prunus avium",
        "icon": "🍒",
        "growth_cycle_days": 115,
        "shelf_life_days": 7,
        "mitidja_priority": False,
    },
    "Squash": {
        "id": "crp_squash",
        "name_en": "Squash / Courgette",
        "name_ar": "كوسة / قرع",
        "name_fr": "Courge / Courgette",
        "scientific_name": "Cucurbita pepo",
        "icon": "🥒",
        "growth_cycle_days": 70,
        "shelf_life_days": 14,
        "mitidja_priority": True,
    },
    "Blueberry": {
        "id": "crp_blueberry",
        "name_en": "Blueberry",
        "name_ar": "توت أزرق",
        "name_fr": "Myrtille",
        "scientific_name": "Vaccinium corymbosum",
        "icon": "🫐",
        "growth_cycle_days": 120,
        "shelf_life_days": 10,
        "mitidja_priority": False,
    },
    "Raspberry": {
        "id": "crp_raspberry",
        "name_en": "Raspberry",
        "name_ar": "توت العليق",
        "name_fr": "Framboise",
        "scientific_name": "Rubus idaeus",
        "icon": "🍓",
        "growth_cycle_days": 110,
        "shelf_life_days": 5,
        "mitidja_priority": False,
    },
    "Soybean": {
        "id": "crp_soybean",
        "name_en": "Soybean",
        "name_ar": "فول الصويا",
        "name_fr": "Soja",
        "scientific_name": "Glycine max",
        "icon": "🫘",
        "growth_cycle_days": 115,
        "shelf_life_days": 90,
        "mitidja_priority": False,
    },
}

# Detailed agronomic data for all 38 classes
DISEASE_KB_DETAILS: Dict[str, Dict[str, Any]] = {
    "Apple___Apple_scab": {
        "name_en": "Apple Scab",
        "name_ar": "جرب التفاح",
        "name_fr": "Tavelure du pommier",
        "pathogen": "Venturia inaequalis (Fungal)",
        "symptoms": "Olive-green to velvety brown/black lesions on leaves and fruit; leaves may twist and drop prematurely.",
        "organic_treatment": [
            "Spray wettable sulfur or Bordeaux/copper soap prior to forecasted rain periods",
            "Rake and compost/destroy fallen leaves in autumn to eliminate overwintering ascospores",
            "Prune interior branches to accelerate leaf drying after morning dew"
        ],
        "chemical_treatment": [
            "Apply myclobutanil, difenoconazole, or captan from green-tip through petal fall"
        ],
        "loss_multiplier": 1.05,
    },
    "Apple___Black_rot": {
        "name_en": "Apple Black Rot (Frogeye Leaf Spot)",
        "name_ar": "العفن الأسود في التفاح",
        "name_fr": "Pourriture noire du pommier",
        "pathogen": "Botryosphaeria obtusa (Fungal)",
        "symptoms": "Circular purple-bordered leaf spots with tan centers ('frogeye' pattern), limb cankers, and firm black fruit rot.",
        "organic_treatment": [
            "Prune out dead wood, fire-blighted twigs, and all mummified fruit hanging on trees",
            "Disinfect pruning shears with 70% alcohol between cuts",
            "Apply copper-based dormant spray before bud swell"
        ],
        "chemical_treatment": [
            "Apply captan or thiophanate-methyl sprays from petal fall through mid-summer"
        ],
        "loss_multiplier": 1.15,
    },
    "Apple___Cedar_apple_rust": {
        "name_en": "Cedar Apple Rust",
        "name_ar": "صدأ التفاح والعرعر",
        "name_fr": "Rouille grillagée du pommier",
        "pathogen": "Gymnosporangium juniperi-virginianae (Fungal)",
        "symptoms": "Bright yellow-orange spots on upper leaf surfaces with tiny black pycnia and tubular projections underneath.",
        "organic_treatment": [
            "Apply liquid sulfur or potassium bicarbonate sprays every 7-10 days from pink bud to early summer",
            "Remove galls from nearby juniper/cedar windbreaks within 300m where possible"
        ],
        "chemical_treatment": [
            "Spray myclobutanil or fenarimol at pink-bud, petal-fall, and 10-day cover stages"
        ],
        "loss_multiplier": 0.95,
    },
    "Apple___healthy": {
        "name_en": "Healthy Apple Leaf",
        "name_ar": "ورقة تفاح سليمة",
        "name_fr": "Feuille de pommier saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Uniform deep green lamina, intact serrated margins, no necrotic or chlorotic lesions.",
        "organic_treatment": [
            "Maintain winter dormant oil + copper sanitation spray",
            "Monitor codling moth and aphids with pheromone/sticky traps"
        ],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Blueberry___healthy": {
        "name_en": "Healthy Blueberry Leaf",
        "name_ar": "ورقة توت أزرق سليمة",
        "name_fr": "Feuille de myrtille saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Glossy green foliage with healthy venation.",
        "organic_treatment": ["Keep soil pH between 4.5 and 5.5 using elemental sulfur or pine needle mulch"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "name_en": "Cherry Powdery Mildew",
        "name_ar": "البياض الدقيقي في الكرز",
        "name_fr": "Oïdium du cerisier",
        "pathogen": "Podosphaera clandestina (Fungal)",
        "symptoms": "White powdery felt patches on young leaves causing upward curling, blistering, and stunted shoot growth.",
        "organic_treatment": [
            "Spray potassium bicarbonate (5g/L) or 1% neem oil emulsion at first sign of white mycelium",
            "Prune water sprouts and dense interior shoots to improve sunlight penetration",
            "Avoid late-season heavy nitrogen applications"
        ],
        "chemical_treatment": [
            "Apply wettable sulfur, quinoxyfen, or tebuconazole starting at shuck fall"
        ],
        "loss_multiplier": 1.0,
    },
    "Cherry_(including_sour)___healthy": {
        "name_en": "Healthy Cherry Leaf",
        "name_ar": "ورقة كرز سليمة",
        "name_fr": "Feuille de cerisier saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Healthy vibrant green cherry leaf.",
        "organic_treatment": ["Maintain balanced drip irrigation and post-harvest pruning"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "name_en": "Corn Gray Leaf Spot (Cercospora)",
        "name_ar": "التبقع الرمادي لأوراق الذرة",
        "name_fr": "Cercosporiose du maïs",
        "pathogen": "Cercospora zeae-maydis (Fungal)",
        "symptoms": "Distinct rectangular, tan-to-gray lesions bounded sharply by parallel leaf veins.",
        "organic_treatment": [
            "Rotate out of corn into legumes or small grains for 1-2 years",
            "Incorporate or compost surface corn debris after harvest to speed decomposition",
            "Apply biological Bacillus subtilis foliar bio-fungicide if humid conditions persist"
        ],
        "chemical_treatment": [
            "Apply pyraclostrobin + epoxiconazole or azoxystrobin between VT (tasseling) and R1 (silking)"
        ],
        "loss_multiplier": 1.15,
    },
    "Corn_(maize)___Common_rust_": {
        "name_en": "Corn Common Rust",
        "name_ar": "صدأ الذرة الشائع",
        "name_fr": "Rouille commune du maïs",
        "pathogen": "Puccinia sorghi (Fungal)",
        "symptoms": "Cinnamon-brown, powdery elongated pustules erupting on both upper and lower leaf surfaces.",
        "organic_treatment": [
            "Plant rust-tolerant maize varieties and plant early to escape peak spore flights",
            "Apply sulfur or copper soap spray on young plants if pustules appear before tassel emergence"
        ],
        "chemical_treatment": [
            "Apply propiconazole or azoxystrobin if pustules cover >3-5% of leaf area prior to silking"
        ],
        "loss_multiplier": 0.95,
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "name_en": "Corn Northern Leaf Blight",
        "name_ar": "لفحة أوراق الذرة الشمالية",
        "name_fr": "Helminthosporiose du maïs",
        "pathogen": "Exserohilum turcicum (Fungal)",
        "symptoms": "Long, elliptical, cigar-shaped grayish-green to tan lesions (3 to 15 cm long) starting on lower leaves.",
        "organic_treatment": [
            "Rotate with non-host crops (potato, bean, clover) and bury infected stover",
            "Eliminate volunteer corn plants early in the season"
        ],
        "chemical_treatment": [
            "Apply triazole or strobilurin fungicide if lesions reach the ear leaf or two leaves below it at tasseling"
        ],
        "loss_multiplier": 1.2,
    },
    "Corn_(maize)___healthy": {
        "name_en": "Healthy Corn Leaf",
        "name_ar": "ورقة ذرة سليمة",
        "name_fr": "Feuille de maïs saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Deep green parallel-veined blade with no pustules or necrotic streaks.",
        "organic_treatment": ["Maintain V6 nitrogen side-dressing and regular weed control"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Grape___Black_rot": {
        "name_en": "Grape Black Rot",
        "name_ar": "العفن الأسود في العنب",
        "name_fr": "Black-rot de la vigne",
        "pathogen": "Guignardia bidwellii (Fungal)",
        "symptoms": "Circular reddish-brown leaf lesions with dark margins and tiny black fruiting bodies (pycnidia) arranged in a ring.",
        "organic_treatment": [
            "Strip and destroy all mummified berries from vines and trellis wires during winter pruning",
            "Cultivate soil under vines before budbreak to bury overwintering mummies",
            "Apply Bordeaux mixture or copper hydroxide before rain events"
        ],
        "chemical_treatment": [
            "Spray myclobutanil, tebuconazole, or mancozeb from 10-cm shoot stage through 4 weeks post-bloom"
        ],
        "loss_multiplier": 1.25,
    },
    "Grape___Esca_(Black_Measles)": {
        "name_en": "Grape Esca (Black Measles)",
        "name_ar": "مرض الإسكا (الحصبة السوداء) في العنب",
        "name_fr": "Esca de la vigne",
        "pathogen": "Phaeomoniella chlamydospora & Phaeoacremonium (Fungal Complex)",
        "symptoms": "Interveinal 'tiger-stripe' chlorosis and reddish-brown necrosis on leaves, with dark spotting on berries.",
        "organic_treatment": [
            "Delay pruning until late winter in dry weather and immediately coat pruning cuts with Trichoderma bio-paste",
            "Surgically remove infected cordons/trunks below stained wood and burn pruned debris"
        ],
        "chemical_treatment": [
            "Apply wound sealant containing approved fungicidal protectants immediately after pruning"
        ],
        "loss_multiplier": 1.35,
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "name_en": "Grape Isariopsis Leaf Blight",
        "name_ar": "لفحة أوراق العنب",
        "name_fr": "Tache angulaire des feuilles de vigne",
        "pathogen": "Pseudocercospora vitis (Fungal)",
        "symptoms": "Irregular angular dark-brown to black spots with yellow halos on older leaves late in the season.",
        "organic_treatment": [
            "Perform basal leaf removal around fruit clusters to improve airflow",
            "Apply copper oxychloride or potassium bicarbonate spray"
        ],
        "chemical_treatment": [
            "Spray mancozeb or strobilurin fungicide if defoliation threatens berry ripening"
        ],
        "loss_multiplier": 1.0,
    },
    "Grape___healthy": {
        "name_en": "Healthy Grape Leaf",
        "name_ar": "ورقة عنب سليمة",
        "name_fr": "Feuille de vigne saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Healthy palmate grape leaf with clean lobes.",
        "organic_treatment": ["Continue canopy shoot positioning and sulfur dusting schedule"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "name_en": "Citrus Greening (Huanglongbing / HLB)",
        "name_ar": "اخضرار الحمضيات (مرض التنين الأصفر)",
        "name_fr": "Maladie du dragon jaune (HLB des agrumes)",
        "pathogen": "Candidatus Liberibacter spp. (Bacterial, Psyllid-transmitted)",
        "symptoms": "Asymmetrical blotchy mottling across leaf veins (unlike symmetric zinc/iron deficiency), yellow shoots, lopsided bitter fruit.",
        "organic_treatment": [
            "Hang yellow sticky traps to monitor Asian/African citrus psyllid vectors immediately",
            "Spray 1-2% horticultural mineral oil or neem oil on new flush to suppress psyllid nymphs",
            "Report and remove confirmed HLB-infected trees to protect surrounding Mitidja citrus orchards"
        ],
        "chemical_treatment": [
            "Coordinate regional psyllid vector control using spinosad, abamectin, or systemic insecticides prior to flush"
        ],
        "loss_multiplier": 1.4,
    },
    "Peach___Bacterial_spot": {
        "name_en": "Peach Bacterial Spot",
        "name_ar": "التبقع البكتيري في الخوخ",
        "name_fr": "Tache bactérienne du pêcher",
        "pathogen": "Xanthomonas arboricola pv. pruni (Bacterial)",
        "symptoms": "Small angular purple-brown spots on leaves whose centers drop out, leaving a tattered 'shot-hole' appearance.",
        "organic_treatment": [
            "Apply fixed copper sprays at autumn leaf drop and late dormant bud swell",
            "Maintain balanced potassium/calcium nutrition and avoid excess nitrogen",
            "Plant windbreaks to reduce wind-blown sand injury that opens entry wounds"
        ],
        "chemical_treatment": [
            "Apply low-rate copper oxychloride or oxytetracycline sprays from shuck split at 10-day intervals"
        ],
        "loss_multiplier": 1.1,
    },
    "Peach___healthy": {
        "name_en": "Healthy Peach Leaf",
        "name_ar": "ورقة خوخ سليمة",
        "name_fr": "Feuille de pêcher saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Smooth lanceolate green peach leaf.",
        "organic_treatment": ["Maintain open-center pruning and dormant copper spray against peach leaf curl"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Pepper,_bell___Bacterial_spot": {
        "name_en": "Bell Pepper Bacterial Spot",
        "name_ar": "التبقع البكتيري في الفلفل",
        "name_fr": "Gale bactérienne du poivron",
        "pathogen": "Xanthomonas euvesicatoria (Bacterial)",
        "symptoms": "Water-soaked dark brown spots with yellow halos on lower leaves, leading to rapid yellowing and leaf drop.",
        "organic_treatment": [
            "Spray fixed copper + biological Bacillus subtilis every 7 days during humid weather",
            "Switch from overhead sprinklers to drip irrigation and mulch beds with black plastic or straw",
            "Soak non-treated seeds in 50°C warm water for 25 minutes before sowing"
        ],
        "chemical_treatment": [
            "Tank-mix copper hydroxide with mancozeb to improve free copper availability"
        ],
        "loss_multiplier": 1.15,
    },
    "Pepper,_bell___healthy": {
        "name_en": "Healthy Bell Pepper Leaf",
        "name_ar": "ورقة فلفل حلو سليمة",
        "name_fr": "Feuille de poivron saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Glossy green ovate leaf with smooth margins.",
        "organic_treatment": ["Maintain steady soil moisture and foliar calcium to prevent blossom-end rot"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Potato___Early_blight": {
        "name_en": "Potato Early Blight",
        "name_ar": "اللفحة المبكرة في البطاطا",
        "name_fr": "Alternariose de la pomme de terre",
        "pathogen": "Alternaria solani (Fungal)",
        "symptoms": "Dark brown circular lesions with concentric 'target-board' rings starting on older lower leaves.",
        "organic_treatment": [
            "Remove heavily spotted lower leaves and avoid nitrogen or phosphorus deficiency stress",
            "Apply copper oxychloride, Bordeaux mixture, or Bacillus amyloliquefaciens bio-fungicide",
            "Allow tubers to cure and skin-set fully before harvest to prevent storage rot"
        ],
        "chemical_treatment": [
            "Apply azoxystrobin, difenoconazole, or mancozeb every 10-14 days from tuber initiation"
        ],
        "loss_multiplier": 1.15,
    },
    "Potato___Late_blight": {
        "name_en": "Potato Late Blight",
        "name_ar": "اللفحة المتأخرة في البطاطا (الميلديو)",
        "name_fr": "Mildiou de la pomme de terre",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "symptoms": "Large water-soaked dark green to black blotches at leaf tips/margins with white cottony sporulation underneath in morning humidity.",
        "organic_treatment": [
            "URGENT: Cut and destroy infected haulms immediately to prevent sporangia from washing down into tubers",
            "Spray protective copper hydroxide or Bordeaux mixture on surrounding healthy foliage",
            "Hill extra soil over potato ridges to shield tubers from spores"
        ],
        "chemical_treatment": [
            "Apply curative systemic oomycete fungicides (cymoxanil + mancozeb, mandipropamid, or fluopicolide) immediately"
        ],
        "loss_multiplier": 1.4,
    },
    "Potato___healthy": {
        "name_en": "Healthy Potato Leaf",
        "name_ar": "ورقة بطاطا سليمة",
        "name_fr": "Feuille de pomme de terre saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Healthy compound potato leaflets.",
        "organic_treatment": ["Continue ridge hilling and monitor humidity/temperature for blight risk"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Raspberry___healthy": {
        "name_en": "Healthy Raspberry Leaf",
        "name_ar": "ورقة توت العليق سليمة",
        "name_fr": "Feuille de framboisier saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Healthy serrated green raspberry leaflet.",
        "organic_treatment": ["Thin canes to 15-20 per linear meter for airflow"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Soybean___healthy": {
        "name_en": "Healthy Soybean Leaf",
        "name_ar": "ورقة فول الصويا سليمة",
        "name_fr": "Feuille de soja saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Healthy trifoliate soybean leaf.",
        "organic_treatment": ["Ensure Rhizobium root nodulation and scout for pod borers"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Squash___Powdery_mildew": {
        "name_en": "Squash Powdery Mildew",
        "name_ar": "البياض الدقيقي في الكوسة والقرع",
        "name_fr": "Oïdium des cucurbitacées",
        "pathogen": "Podosphaera xanthii / Erysiphe cichoracearum (Fungal)",
        "symptoms": "White talcum-like powdery colonies covering upper and lower leaf surfaces, turning leaves yellow then crisp brown.",
        "organic_treatment": [
            "Spray potassium bicarbonate (5g/L) + 0.5% horticultural oil or raw milk dilution (1:9 milk:water) in early morning",
            "Dust or spray wettable sulfur when temperatures are below 30°C",
            "Prune oldest heavily mildewed leaves near the crown to improve airflow"
        ],
        "chemical_treatment": [
            "Apply myclobutanil, triflumizole, or cyflufenamid rotating FRAC groups"
        ],
        "loss_multiplier": 1.05,
    },
    "Strawberry___Leaf_scorch": {
        "name_en": "Strawberry Leaf Scorch",
        "name_ar": "احتراق أوراق الفراولة",
        "name_fr": "Tache pourpre du fraisier",
        "pathogen": "Diplocarpon earlianum (Fungal)",
        "symptoms": "Numerous irregular dark-purple blotches without white centers that coalesce, making the leaf look red/purple and scorched.",
        "organic_treatment": [
            "Mow and remove old infected foliage immediately after final harvest renovation",
            "Use drip irrigation under straw/plastic mulch instead of overhead watering",
            "Spray copper soap or biological Trichoderma / Bacillus bio-fungicide"
        ],
        "chemical_treatment": [
            "Apply captan, thiophanate-methyl, or azoxystrobin at bloom and post-renovation"
        ],
        "loss_multiplier": 1.0,
    },
    "Strawberry___healthy": {
        "name_en": "Healthy Strawberry Leaf",
        "name_ar": "ورقة فراولة سليمة",
        "name_fr": "Feuille de fraisier saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Clean trifoliate strawberry leaf with sharp marginal teeth.",
        "organic_treatment": ["Maintain clean straw mulch and drip fertigation"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
    "Tomato___Bacterial_spot": {
        "name_en": "Tomato Bacterial Spot",
        "name_ar": "التبقع البكتيري في الطماطم",
        "name_fr": "Gale bactérienne de la tomate",
        "pathogen": "Xanthomonas spp. (Bacterial)",
        "symptoms": "Small, greasy, dark-brown to black circular spots (<3 mm) surrounded by yellow halos; leaves scorch and tattered.",
        "organic_treatment": [
            "Prune lower leaves within 25 cm of soil and mulch heavily to stop rain splash",
            "Spray fixed copper hydroxide or biological Bacillus subtilis / bacteriophages every 7 days",
            "Never tie, prune, or harvest plants while foliage is wet with dew or rain"
        ],
        "chemical_treatment": [
            "Apply tank-mix of fixed copper + mancozeb at first symptom appearance"
        ],
        "loss_multiplier": 1.15,
    },
    "Tomato___Early_blight": {
        "name_en": "Tomato Early Blight",
        "name_ar": "اللفحة المبكرة في الطماطم (الألترناريا)",
        "name_fr": "Alternariose de la tomate",
        "pathogen": "Alternaria solani (Fungal)",
        "symptoms": "Brown-black lesions with concentric bullseye rings and surrounding yellow chlorosis starting on oldest basal leaves.",
        "organic_treatment": [
            "Remove infected bottom leaves up to the first fruit cluster and burn/bag them",
            "Mulch soil surface with straw and stake/trellis vines to maximize airflow",
            "Spray copper oxychloride, potassium bicarbonate, or Bacillus amyloliquefaciens"
        ],
        "chemical_treatment": [
            "Apply azoxystrobin, difenoconazole, or chlorothalonil every 7-10 days"
        ],
        "loss_multiplier": 1.15,
    },
    "Tomato___Late_blight": {
        "name_en": "Tomato Late Blight",
        "name_ar": "اللفحة المتأخرة في الطماطم (الميلديو)",
        "name_fr": "Mildiou de la tomate",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "symptoms": "Rapidly expanding pale-green to dark brown/black water-soaked blotches on leaves and stems with white downy ring underneath.",
        "organic_treatment": [
            "URGENT: Uproot and bag severely infected plants on the spot so spores do not blow across the field",
            "Spray surrounding plants thoroughly with Bordeaux mixture or copper hydroxide",
            "Ventilate plastic tunnels immediately in the morning to dry condensation"
        ],
        "chemical_treatment": [
            "Spray mandipropamid, cymoxanil + famoxadone, or propamocarb immediately"
        ],
        "loss_multiplier": 1.4,
    },
    "Tomato___Leaf_Mold": {
        "name_en": "Tomato Leaf Mold",
        "name_ar": "عفن أوراق الطماطم",
        "name_fr": "Cladosporiose de la tomate",
        "pathogen": "Passalora fulva / Fulvia fulva (Fungal)",
        "symptoms": "Pale greenish-yellow spots on upper leaf surfaces paired with olive-green to velvety brown mold directly underneath.",
        "organic_treatment": [
            "Ventilate greenhouse/plasticulture tunnels to keep relative humidity below 85%",
            "Prune lower leaves and wide-space plants to increase air circulation",
            "Apply potassium bicarbonate, sulfur, or copper octanoate"
        ],
        "chemical_treatment": [
            "Apply difenoconazole, chlorothalonil, or cyprodinil in high-humidity greenhouses"
        ],
        "loss_multiplier": 1.05,
    },
    "Tomato___Septoria_leaf_spot": {
        "name_en": "Tomato Septoria Leaf Spot",
        "name_ar": "تبقع سبتوريا في أوراق الطماطم",
        "name_fr": "Septoriose de la tomate",
        "pathogen": "Septoria lycopersici (Fungal)",
        "symptoms": "Numerous small (2-4 mm) circular spots with dark brown borders and tan/gray centers dotted with tiny black pycnidia.",
        "organic_treatment": [
            "Strip infected lower leaves and apply organic straw mulch to block soil-borne spore splash",
            "Spray copper fungicide or Serenade (Bacillus subtilis) every 7-10 days",
            "Practice a 3-year crop rotation away from nightshades (tomato, potato, pepper, eggplant)"
        ],
        "chemical_treatment": [
            "Apply mancozeb, chlorothalonil, or azoxystrobin every 7-10 days during wet periods"
        ],
        "loss_multiplier": 1.1,
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "name_en": "Two-Spotted Spider Mite",
        "name_ar": "العنكبوت الأحمر ذو البقعتين",
        "name_fr": "Acarien jaune tisserand (Tétranyque)",
        "pathogen": "Tetranychus urticae (Arachnid Pest)",
        "symptoms": "Fine yellow/white stippling on upper leaves, bronzing of foliage, and delicate silky webbing on leaf undersides.",
        "organic_treatment": [
            "Wash leaf undersides with a strong water jet and spray 1% cold-pressed neem oil or potassium fatty-acid soap",
            "Release predatory mites (Phytoseiulus persimilis or Amblyseius californicus)",
            "Keep farm tracks damp to reduce road dust on outer rows and prevent drought stress"
        ],
        "chemical_treatment": [
            "Apply selective acaricides (abamectin, bifenazate, or spiromesifen); avoid broad-spectrum pyrethroids that flare mites"
        ],
        "loss_multiplier": 1.1,
    },
    "Tomato___Target_Spot": {
        "name_en": "Tomato Target Spot",
        "name_ar": "التبقع الهدف في الطماطم",
        "name_fr": "Tache cible de la tomate (Corynespora)",
        "pathogen": "Corynespora cassiicola (Fungal)",
        "symptoms": "Brown necrotic lesions with subtle concentric rings and yellow margins that coalesce and cause shot-holes.",
        "organic_treatment": [
            "Prune dense lower canopy to reduce leaf wetness duration",
            "Apply copper hydroxide or biological Trichoderma harzianum foliar spray"
        ],
        "chemical_treatment": [
            "Apply boscalid + pyraclostrobin, fluopyram, or difenoconazole"
        ],
        "loss_multiplier": 1.1,
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name_en": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "name_ar": "فيروس تجعد واصفرار أوراق الطماطم (TYLCV)",
        "name_fr": "Virus des feuilles jaunes en cuillère (TYLCV)",
        "pathogen": "Begomovirus (Viral, transmitted by Bemisia tabaci Whitefly)",
        "symptoms": "Severe upward cupping/curling of small leaves, bright yellow margins, bushy stunted internodes, and flower drop.",
        "organic_treatment": [
            "Bag and uproot infected stunted plants early so whiteflies do not spread the virus to healthy rows",
            "Install 50-mesh insect-proof netting on greenhouse vents and hang yellow sticky traps (1 trap per 10 m²)",
            "Spray neem oil or Beauveria bassiana on leaf undersides to suppress whitefly nymphs"
        ],
        "chemical_treatment": [
            "Control Bemisia tabaci whitefly vectors using cyantraniliprole, flupyradifurone, or pyriproxyfen; plant Ty-resistant hybrids"
        ],
        "loss_multiplier": 1.35,
    },
    "Tomato___Tomato_mosaic_virus": {
        "name_en": "Tomato Mosaic Virus (ToMV)",
        "name_ar": "فيروس موزاييك الطماطم (ToMV)",
        "name_fr": "Virus de la mosaïque de la tomate (ToMV)",
        "pathogen": "Tobamovirus (Viral, mechanically transmitted)",
        "symptoms": "Light and dark green mottled mosaic pattern on leaves, fern-like distortion (shoestringing) in cool weather, internal browning of fruit.",
        "organic_treatment": [
            "Curative: Remove and destroy infected plants immediately without brushing against healthy neighbors",
            "Dip hands and pruning shears in a 20% non-fat milk solution or 10% household bleach between plants",
            "Enforce a strict no-smoking / no-tobacco handling rule in greenhouses and nurseries"
        ],
        "chemical_treatment": [
            "No chemical cure exists for plant viruses; use certified ToMV-resistant varieties (Tm-2² gene) and sterile seed"
        ],
        "loss_multiplier": 1.25,
    },
    "Tomato___healthy": {
        "name_en": "Healthy Tomato Leaf",
        "name_ar": "ورقة طماطم سليمة",
        "name_fr": "Feuille de tomate saine",
        "pathogen": "None (Healthy)",
        "symptoms": "Deep green compound tomato leaf with normal turgor and clean margins.",
        "organic_treatment": ["Maintain regular sucker pruning, staking, and drip irrigation with calcium/potassium balance"],
        "chemical_treatment": ["No chemical treatment needed."],
        "loss_multiplier": 0.0,
    },
}


def get_crop_from_class(class_key: str) -> str:
    """Extracts clean parent crop name from a 38-class key."""
    raw = class_key.split("___")[0]
    return raw.replace("_", " ").strip()


def build_crop_to_indices() -> Dict[str, List[int]]:
    mapping: Dict[str, List[int]] = {}
    for idx, cls_key in enumerate(CLASS_NAMES_38):
        crop = get_crop_from_class(cls_key)
        mapping.setdefault(crop, []).append(idx)
    return mapping


CROP_TO_INDICES = build_crop_to_indices()
