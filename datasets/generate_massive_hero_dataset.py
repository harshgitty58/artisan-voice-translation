import os
import csv
import json
import random
from typing import List, Dict

# Expanded Indian Artisanal Craft Database
# Schema: id, name, category, region, history, material, utility, variations (10 items)

CRAFT_DATABASE = [
    # --- JAMMU & KASHMIR & LADAKH ---
    {
        "id": "kani_shawl",
        "name": "Kashmir Kani Shawl",
        "category": "Textiles",
        "region": "Jammu and Kashmir",
        "history": "Originating in Kanihama and documented in Mughal court records since Emperor Akbar's reign, Kani weaving represents one of the most complex handloom traditions in Asia.",
        "material": "Handcrafted using fine wooden spools called 'kanis' without conventional shuttles, weaving pure mountain Changthangi pashmina into intricate curvilinear jamawar patterns.",
        "utility": "Prized for its whisper-soft drape and intricate double-sided finish, this museum-grade shawl provides regal insulation for high-profile cultural gatherings and weddings.",
        "variations": ["shawl", "stole", "wrap", "jamawar shawl", "winter wrap", "ceremonial stole", "reversible scarf", "collector wrap", "heirloom shawl", "royal pashmina"]
    },
    {
        "id": "kashmir_papier_mache",
        "name": "Kashmiri Papier-Mâché",
        "category": "Art",
        "region": "Jammu and Kashmir",
        "history": "Introduced in the 14th century by the Sufi saint Mir Sayyid Ali Hamadani and patronized by Sultan Zain-ul-Abidin, this craft transformed Persian artistic styles into a Himalayan art form.",
        "material": "Hand-molded from soaked recycled paper pulp and rice binder (sakhtsazi), coated in mineral base plaster, and hand-painted with pure gold leaf and squirrel-hair brushes (naqashi).",
        "utility": "Protected by clear natural varnish for crack-free longevity, these vibrant floral vessels and boxes bring imperial Kashmiri charm to office desks and mantelpieces.",
        "variations": ["decorative box", "coasters set", "flower vase", "hanging bauble", "pen tray", "desk organizer", "trinket bowl", "wall plaque", "bangle set", "collector box"]
    },
    {
        "id": "kashmir_walnut_wood",
        "name": "Kashmir Walnut Wood Carving",
        "category": "Woodwork",
        "region": "Jammu and Kashmir",
        "history": "Thriving in the Kashmir Valley for over five centuries, this architectural woodcraft was historically patronized by Mughal governors to embellish houseboats and summer palaces.",
        "material": "Hand-chiseled from indigenous Juglans regia (walnut) heartwood aged for years, carved using delicate relief and lattice (jali) techniques with zero synthetic veneers.",
        "utility": "Naturally pest-resistant with a deep honey-brown wax luster, this solid timber heirloom adds enduring aristocratic gravitas to sacred home altars and living spaces.",
        "variations": ["carved screen", "jewelry box", "dry fruit tray", "wall panel", "book stand", "coffee table top", "serving tray", "pen stand", "photo frame", "decorative box"]
    },
    {
        "id": "ladakh_clay_tsa_tsa",
        "name": "Ladakhi Tsa-Tsa Clay Mold Art",
        "category": "Ceramics",
        "region": "Ladakh",
        "history": "Deeply woven into trans-Himalayan Buddhist monastic history, Tsa-Tsa tablet molding has been practiced for over a millennium across Ladakh's high-altitude gompas.",
        "material": "Hand-pressed from fine glacial river silt clay enriched with powdered holy herbs and barley grain, kiln-fired or sun-baked before being gilded with mineral tempera.",
        "utility": "Revered as an emblem of mindfulness, clarity, and protective energy, these intricate medallion plaques offer tactile serenity for personal meditation corners and study rooms.",
        "variations": ["buddha plaque", "meditation tablet", "wall medallion", "votive tablet", "monastery amulet", "sacred relief", "study token", "prayer plaque", "table shrine", "zen medallion"]
    },

    # --- HIMACHAL PRADESH & PUNJAB ---
    {
        "id": "kullu_shawl",
        "name": "Kullu Woolen Shawl",
        "category": "Textiles",
        "region": "Himachal Pradesh",
        "history": "Evolving from traditional Kinnauri patterns and formalized in the mid-20th century across the Beas valley, Kullu weaving is an internationally acclaimed GI-tagged heritage.",
        "material": "Handwoven on pit looms using indigenous mountain sheep fleece and merino yarn, inlaid with bright hand-picked geometric weft motifs inspired by Himalayan temple architecture.",
        "utility": "Engineered for breathable thermal comfort, this lightweight woolen drape resists pill formation, making it ideal for brisk morning walks and winter formal wear.",
        "variations": ["shawl", "stole", "muffler", "wrap", "woolen throw", "poncho", "scarf", "winter wrap", "travel shawl", "handloom stole"]
    },
    {
        "id": "chamba_rumal",
        "name": "Chamba Rumal Needlecraft",
        "category": "Textiles",
        "region": "Himachal Pradesh",
        "history": "Flourishing under the hill rajas of Chamba in the 17th century, this double-sided embroidery tradition emerged as a needlework manifestation of Pahari miniature painting.",
        "material": "Embroidered on unbleached, handspun malmal cotton with untwisted silk floss (pat) using the complex 'do-rukha' stitch, producing identical imagery on both front and back.",
        "utility": "Depicting lyrical Raslila and mythological epics with zero visible knots, this heirloom cloth makes an enchanting table centerpiece or framed gallery accent.",
        "variations": ["framed wall art", "ceremonial kerchief", "table centerpiece", "dupatta panel", "pillow cover", "sari border panel", "cushion square", "collector piece", "heritage runner", "wall hanging"]
    },
    {
        "id": "punjabi_jutti",
        "name": "Patiala Punjabi Jutti",
        "category": "Footwear",
        "region": "Punjab",
        "history": "Favored by the royal aristocracy of Patiala and the Mughal nobility since the 16th century, the Punjabi jutti is a timeless cornerstone of northern celebratory dressing.",
        "material": "Crafted from vegetable-tanned buffalo leather, hand-stitched with heavy cotton twines, and lavishly embroidered with dabka, zari, and colored silk thread work.",
        "utility": "Engineered with a symmetrical sole that contours naturally to the foot over time, this flat slip-on provides all-night festive comfort for weddings and celebratory dances.",
        "variations": ["jutti", "khussa", "wedding jutti", "tilla jutti", "mojari footwear", "festive flat", "embroidered slipon", "bridal jutti", "ethnic shoe", "party jutti"]
    },

    # --- RAJASTHAN & GUJARAT ---
    {
        "id": "sanganeri_print",
        "name": "Sanganeri Hand Block Print",
        "category": "Textiles",
        "region": "Rajasthan",
        "history": "Flourishing along the Sanjharia river since the 16th-century Kachwaha Rajput era, Sanganer emerged as a royal center for the world's most delicate block printing.",
        "material": "Hand-stamped onto pure cambric cotton using hand-carved teakwood blocks dipped in natural river-rinsed dyes, characterized by distinct off-white backgrounds.",
        "utility": "Featuring gossamer feather-light breathability and dainty botanical booti patterns, this summer textile maintains cooling comfort during humid and tropical climates.",
        "variations": ["saree", "dupatta", "running fabric", "bedsheet set", "kurta set", "stole", "table cloth", "cushion cover", "scarf", "summer wrap"]
    },
    {
        "id": "thewa_art",
        "name": "Pratapgarh Thewa Glasswork",
        "category": "Jewelry",
        "region": "Rajasthan",
        "history": "Invented in the 1770s by master goldsmith Nathuji Soni under the royal patronage of the Maharawat of Pratapgarh, Thewa is an closely guarded secret craft of Rajasthan.",
        "material": "Created by laser-fine hand-chiseled 23-karat pure gold foil fused seamlessly over treated, molten Belgian glass wafers through controlled charcoal heating.",
        "utility": "Displaying intricate miniature court, hunting, and floral tableaus bathed in emerald and ruby glass hues, this pendant jewelry radiates regal luxury at milestone events.",
        "variations": ["pendant", "necklace", "brooch", "earrings set", "cufflinks", "ring", "bracelet", "trinket box lid", "choker center", "statement jewel"]
    },
    {
        "id": "pokhran_pottery",
        "name": "Pokhran Red Clay Pottery",
        "category": "Ceramics",
        "region": "Rajasthan",
        "history": "Practiced for centuries across the harsh Thar desert terrain, Pokhran earthenware was developed to store and chill water amidst extreme arid temperatures.",
        "material": "Wheel-thrown from local iron-rich desert silt and white clay, decorated with geometric slip lines and wood-fired in inverted earth kilns without lead glazes.",
        "utility": "Featuring natural microporous breathability that chills drinking water by 5 degrees purely through evaporation, this earthy terracotta brings healthy utility to modern pantries.",
        "variations": ["water matka", "kulhad set", "planter", "serving jug", "spice jar", "terracotta bowl", "curd setting pot", "table vase", "tea mug", "cooking handi"]
    },
    {
        "id": "rogan_art",
        "name": "Nirona Rogan Art",
        "category": "Art",
        "region": "Gujarat",
        "history": "Preserved by a single Khatri family lineage in Nirona village for over three centuries, Rogan painting is one of India's rarest endangered artistic traditions.",
        "material": "Crafted from cold-pressed castor oil boiled for 48 hours into a sticky jelly, mixed with natural mineral pigments, and drawn onto cloth using a metal stylus without direct touch.",
        "utility": "Exhibiting mesmerizing symmetrical floral and Tree of Life motifs that dry permanently into the weave, this textile art forms an exquisite conversation piece for walls.",
        "variations": ["wall hanging", "framed art piece", "saree motif panel", "cushion cover", "table runner", "silk stole", "clutch purse", "fabric panel", "shawl border", "accent panel"]
    },
    {
        "id": "patan_patola",
        "name": "Patan Double Ikat Patola",
        "category": "Textiles",
        "region": "Gujarat",
        "history": "Patronized in the 12th century by King Kumarpala of the Solanki dynasty, Patan Patola represents the zenith of mathematical precision in worldwide textile history.",
        "material": "Woven on sloping teakwood looms from 100% pure mulberry silk threads that are individually resist-dyed in both warp and weft before weaving begins.",
        "utility": "Completely identical on both front and reverse sides with unfading vegetable dyes, this indestructible royal silk endures for generations without losing its crisp geometric vibrancy.",
        "variations": ["saree", "dupatta", "stole", "wall hanging", "bridal drape", "handloom fabric", "ceremonial wrap", "heirloom textile", "silk panel", "festive scarf"]
    },
    {
        "id": "sankheda_furniture",
        "name": "Sankheda Lacquered Woodcraft",
        "category": "Woodwork",
        "region": "Gujarat",
        "history": "Developed in the mid-19th century in Chhota Udaipur district, Sankheda lathe-turned furniture became an indispensable symbol of auspicious Gujarati domestic architecture.",
        "material": "Hand-turned on lathes from solid teakwood (Sagwan), burnished with natural lac resins, and decorated using tin-foil paintings topped with transparent golden varnishes.",
        "utility": "Weather-resistant, chip-proof, and gleaming with a golden amber luster, this traditional furniture adds welcoming regal presence to home entrances, verandas, and puja spaces.",
        "variations": ["low stool (bajot)", "rocking chair", "swing (jhula)", "temple chair", "side table", "corner stand", "pooja set stool", "decorative mirror", "armchair", "footstool"]
    },

    # --- UTTAR PRADESH & BIHAR ---
    {
        "id": "firozabad_glass",
        "name": "Firozabad Blown Glassware",
        "category": "Ceramics",
        "region": "Uttar Pradesh",
        "history": "Tracing its glassblowing origins to 16th-century Mughal royal ateliers, Firozabad developed into the celebrated glass craftsmanship capital of South Asia.",
        "material": "Mouth-blown and hand-shaped from pure silica sand and soda ash at 1400 degrees Celsius, finished with metallic oxides for jewel-toned translucency without industrial molds.",
        "utility": "Featuring exceptional optical clarity, heat tolerance, and bright refraction, these handcrafted glasswares bring vintage bohemian color to banquet dining and living room decor.",
        "variations": ["blown vase", "hanging lantern", "water carafe", "drinking tumbler set", "candle holder", "chandelier bell", "serving bowl", "perfume bottle", "table decanter", "accent globe"]
    },
    {
        "id": "khurja_pottery",
        "name": "Khurja Glazed Ceramics",
        "category": "Ceramics",
        "region": "Uttar Pradesh",
        "history": "Initiated during the reign of Sultan Mohammad bin Tughlaq by immigrant potters, Khurja evolved over 600 years into India's premier ceramic town.",
        "material": "Wheel-thrown and slip-cast from refined ball clay, feldspar, and quartz, hand-painted with cobalt floral vines and high-fired at 1200 degrees Celsius with lead-free glazes.",
        "utility": "Completely non-porous, microwave-safe, and chip-resistant, these vibrant dinnerware and garden pots marry historic Mughal aesthetics with rigorous modern kitchen utility.",
        "variations": ["dinner plate set", "serving bowl", "tea cup set", "garden planter", "storage jar (barni)", "soup mug", "decorative jug", "milk pitcher", "pasta bowl", "ceramic teapot"]
    },
    {
        "id": "kannauj_attar",
        "name": "Kannauj Deg-Bhapka Perfumery",
        "category": "Art",
        "region": "Uttar Pradesh",
        "history": "Flourishing under Emperor Harsha in the 7th century and later courted by Awadh royalty, Kannauj is the historic perfume capital maintaining ancient hydro-distillation.",
        "material": "Distilled in copper stills (degs) using wood fires, capturing fresh damask rose petals or monsoon rain-baked earth (mitti) into a base of 100% pure sandalwood oil.",
        "utility": "Completely alcohol-free, deeply soothing, and enduring on the skin for over 24 hours, this natural attar offers luxurious holistic aromatics for festive and sacred ceremonies.",
        "variations": ["mitti attar", "gulab attar", "khus extract", "shamama attar", "oudh concentrate", "motia oil", "kewra attar", "musk amber", "jasmine perfume", "sacred rollon"]
    },
    {
        "id": "bhagalpuri_tussar",
        "name": "Bhagalpur Tussar Silk",
        "category": "Textiles",
        "region": "Bihar",
        "history": "Cultivated for over a century across the fertile banks of the Ganges in Bhagalpur, this wild silk tradition represents the core of Bihar's handloom economy.",
        "material": "Hand-reeled from wild Antheraea mylitta silkworm cocoons fed on Asan and Arjun trees, handwoven on pit looms without boiling the pupae alive (peace silk).",
        "utility": "Celebrated for its coarse golden sheen, porous thermal regulation, and structural body, this fabric resists creasing and provides commanding authority for corporate and formal wear.",
        "variations": ["saree", "kurta fabric", "dupatta", "running yardage", "formal blazer fabric", "stole", "mens kurta", "suit set", "handloom scarf", "festive saree"]
    },
    {
        "id": "sujini_embroidery",
        "name": "Muzaffarpur Sujini Embroidery",
        "category": "Textiles",
        "region": "Bihar",
        "history": "Originating in the 18th century as a rural maternal quilting tradition, Sujini evolved into a powerful textile medium for folk storytelling across Muzaffarpur.",
        "material": "Layered from repurposed soft muslin or tussar silk, meticulously quilted with thousands of fine running stitches using red and black cotton embroidery threads.",
        "utility": "Lightweight, breathable, and deeply comforting against sensitive skin, this textured coverlet adds artisanal warmth as an all-season throw or conversational wall tapestry.",
        "variations": ["baby quilt", "wall hanging", "cushion cover", "throw blanket", "table runner", "bed coverlet", "tote bag panel", "dupatta accent", "jacket fabric", "lap blanket"]
    },

    # --- MADHYA PRADESH & CHHATTISGARH ---
    {
        "id": "bagh_print",
        "name": "Bagh Hand Block Print",
        "category": "Textiles",
        "region": "Madhya Pradesh",
        "history": "Practiced for over 400 years by the Muslim Khatri community along the mineral-rich Bagh river, this tribal-influenced block printing is renowned for its bold geometry.",
        "material": "Hand-stamped on unbleached cotton using relief-carved teakwood blocks and natural dyes made from corroded iron scrap, alum, and pomegranate rinds washed in river currents.",
        "utility": "Boasting vivid, wash-fast contrasting red and black geometric lattices, this breathable natural fabric provides striking elegance for casual daywear and office attire.",
        "variations": ["saree", "dupatta", "bedcover", "kurta fabric", "stole", "table runner", "cushion cover", "scarf", "dress material", "mens shirt fabric"]
    },
    {
        "id": "tikamgarh_bell_metal",
        "name": "Tikamgarh Bell Metal Casting",
        "category": "Metalwork",
        "region": "Madhya Pradesh",
        "history": "Supported by the Bundela rulers of Orchha since the 17th century, Tikamgarh casting preserves pristine lost-wax metal artistry across the Bundelkhand plateau.",
        "material": "Molded using local beeswax and clay cores, poured with a resonant alloy of copper and tin (kansa), and finished with manual chisels without power tools.",
        "utility": "Producing heavy, solid devotional sculptures with an enduring acoustic resonance and golden patina, these sacred idols serve as generational family heirlooms.",
        "variations": ["radha krishna idol", "dancing peacock", "horse sculpture", "puja diya", "temple bell", "decorative bowl", "elephant figurine", "urli vessel", "candle stand", "wall relief"]
    },
    {
        "id": "bastar_bell_metal",
        "name": "Bastar Dhokra Lost-Wax Metal",
        "category": "Metalwork",
        "region": "Chhattisgarh",
        "history": "Practiced continuously by the Ghadwa tribal craftsmen of the Bastar forests, this ancient lost-wax technique shares direct metallurgical lineage with Harappan art.",
        "material": "Created by winding fine beeswax threads over an ant-hill clay core, encased in river loam, and replaced with molten brass-bronze over open charcoal pit kilns.",
        "utility": "Characterized by slender, elongated folk figures of musicians and forest animals, each piece is a one-of-a-kind sculptural masterpiece for earthy, contemporary home decor.",
        "variations": ["tribal musician", "deer figurine", "bull sculpture", "candle stand", "hanging diya", "wall panel", "table showpiece", "oil lamp", "door handle", "ceremonial vessel"]
    },
    {
        "id": "bastar_kosa_silk",
        "name": "Champa Bastar Kosa Silk",
        "category": "Textiles",
        "region": "Chhattisgarh",
        "history": "Gathered deep inside the sal forests of Chhattisgarh by tribal communities, Kosa silk weaving has anchored royal wedding trousseaus in central India for centuries.",
        "material": "Extracted from wild tropical silkworm cocoons (Antheraea pernyi), hand-reeled on earthen pots, and handwoven on pit looms using organic natural mordants.",
        "utility": "Distinguished by its crisp texture, dull natural metallic gold sheen, and cooling breathability, this elite handloom fabric commands respect at formal symposiums and weddings.",
        "variations": ["saree", "dupatta", "stole", "blazer fabric", "running yardage", "kurta piece", "mens stole", "festive drape", "handloom shawl", "formal fabric"]
    },

    # --- ODISHA & WEST BENGAL ---
    {
        "id": "cuttack_tarakasi",
        "name": "Cuttack Silver Filigree (Tarakasi)",
        "category": "Jewelry",
        "region": "Odisha",
        "history": "Refined over 500 years in the historic millennium city of Cuttack, Tarakasi was patronized by the Gajapati rulers and influenced by maritime trade with ancient Kalinga.",
        "material": "Formed from 99.9% pure silver drawn into gossamer-thin wires finer than hair, crimped into hairspring coils, and hand-soldered into gossamer openwork lace without stamping.",
        "utility": "Incomparably light, luminous, and tarnish-resistant, this jewelry and miniature royal boat art brings delicate, regal sophistication to bridal couture and formal suites.",
        "variations": ["filigree earrings", "silver brooch", "choker necklace", "peacock brooch", "silver boat (boita)", "hair pin", "bangle", "puja vermilion box", "trinket box", "cufflink set"]
    },
    {
        "id": "konark_stone_carving",
        "name": "Konark Sandstone Sculpture",
        "category": "Stone Carving",
        "region": "Odisha",
        "history": "Carried down directly by descendants of the 13th-century artisan guilds who carved the Konark Sun Temple and Jagannath Temple under King Narasimhadeva I.",
        "material": "Hand-chiseled from durable regional khondalite, chlorite, and pink sandstone using hardened tempered chisels and wooden mallets without mechanical cutters.",
        "utility": "Weatherproof and practically eternal across generations, these deeply detailed sculptures of celestial dancers and deities bring ancient temple sanctity to gardens and foyers.",
        "variations": ["sun temple wheel", "alasakanya statue", "ganesha relief", "garden sculpture", "wall plaque", "temple arch panel", "buddha bust", "decorative pillar", "pedestal", "foyer icon"]
    },
    {
        "id": "baluchari_saree",
        "name": "Bishnupur Baluchari Silk",
        "category": "Textiles",
        "region": "West Bengal",
        "history": "Pioneered during the 18th century under the patronage of Nawab Murshid Quli Khan and perfected in Bishnupur by Malla kings, Baluchari is a narrative textile phenomenon.",
        "material": "Woven from 100% pure mulberry silk on jacquard punch looms, featuring weft brocading with untwisted silk yarns depicting mythological scenes on the grand pallu.",
        "utility": "Featuring complete epic storylines from the Ramayana and Mahabharata woven across its borders, this opulent silk drape serves as a glorious bridal and festival statement piece.",
        "variations": ["saree", "bridal saree", "pallu wall hanging", "silk dupatta", "running fabric", "stole", "framing panel", "wedding drape", "ceremonial saree", "silk wrap"]
    },
    {
        "id": "bankura_terracotta",
        "name": "Panchmura Terracotta Horse",
        "category": "Ceramics",
        "region": "West Bengal",
        "history": "Originating as sacred votive offerings for village shrines across rural Rarh Bengal, the Bankura horse has stood as the proud national logo of Indian handicrafts for decades.",
        "material": "Wheel-thrown in separate hollow segments from nutrient-rich alluvial clay, assembled by hand with symmetrical pointed ears, and wood-fired to an earthy burnt terracotta red.",
        "utility": "Possessing a distinctively proud silhouette with erect ears and graceful arching neck, this iconic folk art piece injects rustic sophistication into modern console tables.",
        "variations": ["bankura horse pair", "standing elephant", "wall hanging plaque", "terracotta mask", "terracotta planter", "garden horse figure", "table showpiece", "festive diya", "miniature horse", "decor vessel"]
    },
    {
        "id": "purulia_chhau_mask",
        "name": "Purulia Chhau Dance Mask",
        "category": "Art",
        "region": "West Bengal",
        "history": "Developed in Charida village across the Bagmundi hills, these dramatic masks have energized the acrobatic UNESCO-recognized tribal martial dance of Chhau for generations.",
        "material": "Layered over clay molds with paper pulp, river mud, and cloth, smoothed with fine chalk powder (khari), and hand-painted with vibrant acrylics trimmed in foil plumage.",
        "utility": "Radiating theatrical heroism and fierce mythological energy, these colorful masks transform stark accent walls into dynamic galleries of Indian performing folk art.",
        "variations": ["durga mask", "mahishasura mask", "shiva mask", "peacock mask", "tribal warrior mask", "miniature wall mask", "lion mask", "ganesha mask", "kartikeya mask", "decor mask"]
    },

    # --- NORTH-EASTERN STATES ---
    {
        "id": "sualkuchi_pat_silk",
        "name": "Sualkuchi Pat Silk",
        "category": "Textiles",
        "region": "Assam",
        "history": "Anchored in the craft town of Sualkuchi—celebrated as the Manchester of Assam since the 11th-century Pala dynasty—this silk was the royal attire of Ahom monarchs.",
        "material": "Reeled from indigenous Bombyx textor mulberry silkworms, handwoven on traditional frame looms with intricate Kingkhap (lion) and peacock patterns woven in gold yarn.",
        "utility": "Characterized by its radiant pearl-white luster and crisp structural elegance, this celebratory silk drape stays remarkably pristine and wrinkle-resistant through long banquets.",
        "variations": ["mekhela chador", "saree", "dupatta", "stole", "kurta fabric", "festive wrap", "bridal mekhela", "ceremonial drape", "silk scarf", "handloom fabric"]
    },
    {
        "id": "longpi_black_pottery",
        "name": "Manipur Longpi Hamtei Pottery",
        "category": "Ceramics",
        "region": "Manipur",
        "history": "Crafted exclusively by the Tangkhul Naga tribe of Longpi village for over a millennium, this ancient earthenware was once reserved for tribal royalty and warrior feasts.",
        "material": "Hand-molded entirely without a potter's wheel from ground black serpentinite rock and weathered clay, polished using broad leaves and wild tree bark, and open-pit fired.",
        "utility": "Non-toxic, naturally matte black, and heat-retentive for hours, this exceptional stoneware cooks stews to perfection and provides high-end minimalist tabletop aesthetics.",
        "variations": ["cooking pot", "serving kettle", "coffee mug set", "soup bowl", "tea cup set", "table planter", "water jug", "casserole dish", "table plate", "decorative vase"]
    },
    {
        "id": "mizo_puan",
        "name": "Mizo Puan Handloom Weave",
        "category": "Textiles",
        "region": "Mizoram",
        "history": "Intrinsically bound to Mizo heritage and matrimonial rituals, every distinct Puan weave encodes ancient tribal lineage, bravery, and geographic origin in its colors.",
        "material": "Tightly woven by tribal women on traditional back-strap loin looms using hand-carded cotton, dyed with deep natural plant roots into signature red, white, and black bands.",
        "utility": "Densely woven and wind-resistant with a tactile ribbed texture, this wrap offers dependable outdoor warmth and commands admiration when styled as an artisanal skirt or throw.",
        "variations": ["puanchei wrap", "shawl", "stole", "table runner", "tapestry panel", "cushion cover", "throw blanket", "scarf", "ceremonial wrap", "handloom skirt length"]
    },
    {
        "id": "naga_chakesang_shawl",
        "name": "Chakhesang Naga Shawl",
        "category": "Textiles",
        "region": "Nagaland",
        "history": "Traditionally earned through social prestige and prowess in the highlands of Nagaland, this GI-tagged textile reflects the fierce dignity and spirit of Naga tribes.",
        "material": "Handwoven on back-strap loin looms using indigenous nettle fiber (tsungko) and local mountain wool, accented with hand-twisted fringes and authentic geometric bar embroidery.",
        "utility": "Incredibly durable, insulating, and water-repellent, this heavy tribal wrap brings rugged earthy character to cool autumn evenings and makes an exceptional rustic throw.",
        "variations": ["shawl", "stole", "wall hanging", "couch throw", "tribal wrap", "cushion cover set", "runner", "ceremonial cloth", "scarf", "collector textile"]
    },
    {
        "id": "tripura_bamboo_screen",
        "name": "Tripura Splint Bamboo Craft",
        "category": "Bamboo/Cane",
        "region": "Tripura",
        "history": "Harnessing the lush muli bamboo hills of Tripura, this refined weaving technique was patronized by the Manikya kings to craft lightweight palace blinds and interior fans.",
        "material": "Meticulously hand-sliced into micro-thin pliable bamboo splints (kami), hand-interlaced with organic cotton thread warp without nails, metal wires, or synthetic coats.",
        "utility": "Naturally insect-resistant, pliable, and dust-repellent, these sustainable rollable blinds filter harsh glare into soothing diffuse golden light for eco-friendly modern homes.",
        "variations": ["window blind", "table mat set", "floor runner", "wall screen", "room divider panel", "placemat set", "hanging lamp shade", "fruit basket", "file folder", "fan"]
    },

    # --- MAHARASHTRA & GOA ---
    {
        "id": "sawantwadi_lacquer",
        "name": "Sawantwadi Lacquerware Ganjifa",
        "category": "Woodwork",
        "region": "Maharashtra",
        "history": "Patronized in the 18th century by the Bhonsle dynasty of Sawantwadi, this courtly craft preserved the ancient circular Dashavatara playing card art of royal Maharashtra.",
        "material": "Hand-carved from seasoned Indian cork wood (pango), lacquered smoothly using natural resin washes, and miniature-painted with natural mineral watercolours.",
        "utility": "Displaying intricate mythological portraits with a high-buff lacquer gloss that repels moisture, these pieces function as interactive art games or framed wall treasures.",
        "variations": ["ganjifa cards set", "round jewelry box", "wooden toy set", "dining napkin rings", "fruit bowl", "candle stand", "wall plaque", "coaster set", "pen stand", "collector box"]
    },
    {
        "id": "himroo_shawl",
        "name": "Aurangabad Himroo Weave",
        "category": "Textiles",
        "region": "Maharashtra",
        "history": "Brought to Daulatabad when Sultan Muhammad bin Tughlaq shifted his capital in the 14th century, Himroo emerged as an affordable, breathable royal alternative to pure silk kinkhwab.",
        "material": "Handwoven on complex multi-treadle draw looms using a unique extra-weft technique that interweaves fine lustrous silk yarn with soft breathable combed cotton warp.",
        "utility": "Featuring Ajanta cave-inspired floral arabesques and Persian medallions, this dual-faced fabric offers feather-soft warmth and aristocratic grace for evening social galas.",
        "variations": ["shawl", "stole", "sherwani fabric", "dupatta", "cushion cover", "throw", "scarf", "bed runner", "jacket length", "festive wrap"]
    },
    {
        "id": "goan_azulejos",
        "name": "Goan Azulejo Ceramic Tiles",
        "category": "Ceramics",
        "region": "Goa",
        "history": "Absorbed during the 16th century via Portuguese maritime voyages and rooted in Goan architectural identity, Azulejos grace the entrances of heritage mansions in Old Goa.",
        "material": "Molded from terracotta clay tiles, coated with white tin glaze, hand-painted with cobalt blue mineral oxides, and fired in muffle kilns at high temperatures.",
        "utility": "Waterproof, fade-proof against harsh tropical monsoon sunlight, and easily scrubbed, these vibrant tiles personalize family nameplates and kitchen splashbacks with coastal charm.",
        "variations": ["custom nameplate", "decorative wall tile", "coaster set", "tile mural", "trivet", "kitchen border tile", "accent table top", "framed tile art", "house number tile", "patio plaque"]
    },

    # --- KARNATAKA, TELANGANA, ANDHRA PRADESH ---
    {
        "id": "kinhal_toys",
        "name": "Kinhal Wood & Gesso Craft",
        "category": "Woodwork",
        "region": "Karnataka",
        "history": "Flourishing under the patronage of the Vijayanagara Empire and preserved by the Chitragar community, Kinhal woodcraft decorated the royal palanquins of Hampi.",
        "material": "Hand-chiseled from lightweight softwood, covered with a heritage gesso paste made of tamarind seed powder and pebble lime, and gilded with vibrant paints.",
        "utility": "Possessing a distinct antique enamel shine and rich sculptural depth, these traditional deity and bird figurines introduce regal South Indian heritage to living room consoles.",
        "variations": ["garuda figurine", "peacock showpiece", "cradle toy", "wall bracket", "kamadhenu idol", "festive chowki", "wall panel", "decorative idol", "collector puppet", "heritage plaque"]
    },
    {
        "id": "navalgund_jamalam",
        "name": "Navalgund Jamalam Dhurrie",
        "category": "Textiles",
        "region": "Karnataka",
        "history": "Initiated in the 16th century by immigrant weavers fleeing the fall of the Vijayanagara Empire, Navalgund dhurrie weaving is an endangered GI-tagged heritage of Dharwad.",
        "material": "Hand-knotted on vertical looms by women artisans using pure coarse cotton yarn, woven into geometric interlocks dyed with brilliant yellow, green, and deep maroon.",
        "utility": "Displaying the signature peacock (mayura) and temple tower (gopura) designs with heavy reversible durability, this robust floor textile endures decades of heavy foot traffic.",
        "variations": ["dhurrie rug", "floor runner", "prayer mat", "hall carpet", "bedside rug", "cushion cover", "wall tapestry", "accent mat", "yoga durrie", "dining area rug"]
    },
    {
        "id": "gadwal_saree",
        "name": "Gadwal Handloom Saree",
        "category": "Textiles",
        "region": "Telangana",
        "history": "Cultivated under the royal patronage of the Gadwal Samsthanam since the 18th century, this textile marvel was designed to fold to the compactness of a matchbox.",
        "material": "Engineered with a lightweight pure cotton body seamlessly united to pure mulberry silk borders and pallu using the miraculous historic 'kupiadam' interlocked weft technique.",
        "utility": "Offering the breathable cooling comfort of crisp cotton across the body while flaunting heavy gold zari silk borders, it is the ultimate temple visit and wedding saree.",
        "variations": ["saree", "half saree", "dupatta", "bridal saree", "stole", "traditional saree", "festive silk", "korvai drape", "running yardage", "handloom fabric"]
    },
    {
        "id": "machilipatnam_kalamkari",
        "name": "Machilipatnam Block Kalamkari",
        "category": "Textiles",
        "region": "Andhra Pradesh",
        "history": "Traded extensively with the Persian Gulf and European empires from the ancient port of Masulipatnam under Golconda sultanate patronage, this is India's premier block-dyed textile.",
        "material": "Printed on unbleached cotton using hand-chiseled wooden blocks, treated with buffalo milk and myrobalan nuts, and washed in flowing canal waters to set organic indigo and madder.",
        "utility": "Embellished with the timeless Persian Tree of Life and floral trellises that never bleed or fade, this soft drape adds organic botanical luxury to apparel and home tapestries.",
        "variations": ["saree", "dupatta", "bedsheet set", "table runner", "curtain fabric", "cushion cover", "fabric yardage", "stole", "dining placemat set", "wall hanging"]
    },
    {
        "id": "dharmavaram_silk",
        "name": "Dharmavaram Brocade Silk",
        "category": "Textiles",
        "region": "Andhra Pradesh",
        "history": "Flourishing in Anantapur district for two centuries, Dharmavaram silk weaving was cultivated to supply South Indian royal courts with opulent ceremonial silk regalia.",
        "material": "Handwoven from pure 100% twisted mulberry silk threads, woven with broad, contrast shaded gold zari pallus displaying Lepakshi temple architectural motifs.",
        "utility": "Heavy, rich, and featuring a distinctive dual-shade metallic sheen, this majestic bridal silk holds its pleats crisply throughout hours of traditional Hindu wedding rituals.",
        "variations": ["bridal saree", "traditional saree", "silk lehenga", "wedding drape", "half saree set", "dupatta", "silk fabric", "festive saree", "temple silk", "handloom saree"]
    },

    # --- TAMIL NADU & KERALA ---
    {
        "id": "thanjavur_pith_work",
        "name": "Thanjavur Netti Pith Craft",
        "category": "Woodwork",
        "region": "Tamil Nadu",
        "history": "Originating under the Nayaka and Maratha kings of Thanjavur, this delicate sculpting tradition adorned royal miniature models of the magnificent Brihadeeswara Temple.",
        "material": "Carved with scalpel precision from the dried spongy core of the aquatic swamp reed Aeschynomene aspera (netti), retaining an unblemished natural ivory-white sheen.",
        "utility": "Feather-light, naturally pest-resistant, and extraordinarily detailed under glass displays, these miniature models serve as elite architectural centerpieces for curated art collections.",
        "variations": ["temple model", "brihadeeswara model", "carved chariot", "peacock sculpture", "shrine showcase", "glass-encased idol", "wall hanging", "gift miniature", "art trophy", "showpiece"]
    },
    {
        "id": "nachiarcoil_lamp",
        "name": "Nachiarcoil Bell Metal Brass Lamp",
        "category": "Metalwork",
        "region": "Tamil Nadu",
        "history": "Perfected over 150 years in Thanjavur district by the Pathar community, these towering ritual lamps (Annam kuthu vilakku) illuminate South Indian temple sanctums.",
        "material": "Sand-cast from virgin bell-brass using local pale river sand (vandal man), intricately turned on manual chucks, and hand-chiseled with the mythical hamsa bird topper.",
        "utility": "Possessing a stable weighted base that prevents oil spills and a lustrous mirror polish, this sacred lamp radiates auspicious golden warmth during daily prayers and Diwali.",
        "variations": ["kuthu vilakku lamp", "peacock lamp", "standing deepam", "puja lamp", "diwali oil lamp", "temple lantern", "hanging bell lamp", "brass diya", "pooja thali lamp", "ceremonial lamp"]
    },
    {
        "id": "aranmula_mirror",
        "name": "Aranmula Kannadi Front-Surface Mirror",
        "category": "Metalwork",
        "region": "Kerala",
        "history": "Guarded as a sacred metallurgical family secret since the 16th century in Aranmula village, this mirror was declared a primary royal insignia of Travancore kings.",
        "material": "Hand-cast from an enigmatic copper-tin bronze alloy without silvered glass, ground by hand on wooden planks with emery powder and velvet for weeks to reach specular reflection.",
        "utility": "Providing an optically flawless front-surface reflection without secondary refraction distortions, this auspicious mirror is believed to bestow prosperity and ward off negative aura.",
        "variations": ["valkannadi mirror", "hand mirror", "desk mirror", "wall hanging mirror", "ceremonial mirror", "brass frame mirror", "collector mirror", "temple gift mirror", "heirloom mirror", "pooja mirror"]
    },
    {
        "id": "kerala_bell_metal_urli",
        "name": "Payyanur Bell Metal Urli",
        "category": "Metalwork",
        "region": "Kerala",
        "history": "Cast by the Moosari artisan guilds of Kerala for centuries, the wide-rimmed urli is an ancient staple of ayurvedic concoctions and temple feast preparations.",
        "material": "Solid cast from traditional high-tin bell metal bronze (kansa) using lost-wax and charcoal sand casting, hand-turned and smoothed with stone abrasives to a golden glow.",
        "utility": "Retaining heat evenly while non-reactive with essential oils, this magnificent bowl serves as an opulent floral floating vessel for hotel lobbies, living rooms, and spas.",
        "variations": ["urli bowl", "floating flower vessel", "ayurvedic cooking bowl", "traditional urli", "brass urli", "carved rim bowl", "water centerpiece", "pooja bowl", "foyer urli", "accent bronze bowl"]
    },
    {
        "id": "bengal_sholapith",
        "name": "Kumartuli Sholapith Floral Art",
        "category": "Art",
        "region": "West Bengal",
        "history": "Originating in ancient Bengal as sacred ritual adornments for deity idols, Sholapith artisans have sculpted divine wedding topors and Durga canopies for centuries.",
        "material": "Painstakingly cut using razor-fine blades from the soft white fibrous inner core of the wild marsh herb shola, assembled without artificial bleached chemicals.",
        "utility": "Feather-light, snow-white, and completely biodegradable, these intricate floral garlands and crowns add ethereal spiritual beauty to festive home altars and wedding ceremonies.",
        "variations": ["wedding topor", "durga crown (mukut)", "hanging floral chain", "decorative wall medallion", "shola bird sculpture", "altar garland", "pooja showpiece", "festive wreath", "mandap decor", "gift centerpiece"]
    }
]

# Duplicate logic to ensure it multiplies properly for generation
EXTENDED_DATABASE = list(CRAFT_DATABASE)
for craft in CRAFT_DATABASE:
    alt_craft = dict(craft)
    alt_craft["id"] = craft["id"] + "_alt"
    alt_craft["name"] = "Authentic " + craft["name"]
    EXTENDED_DATABASE.append(alt_craft)

def generate_hero_dataset():
    samples = []
    sample_id = 1
    
    # Informal raw input prefixes to simulate user/artisan speech without prices
    prefixes = [
        "handmade {craft_name}, {variation}",
        "{craft_name} {variation}",
        "pure {craft_name} {variation}",
        "authentic {craft_name} {variation}",
        "traditional {craft_name} {variation}",
        "this is a {craft_name} {variation}",
        "beautiful {variation} of {craft_name}",
        "हाथ का बना {craft_name} {variation}", # Hindi prefix
        "असली {craft_name} {variation}",       # Hindi prefix
        "pure handloom {craft_name} {variation}"
    ]

    for craft in EXTENDED_DATABASE:
        for variation in craft["variations"]:
            # Pick a random prefix
            prefix = random.choice(prefixes)
            raw_input = prefix.format(craft_name=craft["name"].lower(), variation=variation.lower())
            
            line1 = craft["history"]
            line2 = craft["material"]
            line3 = craft["utility"]
            
            full_description = f"{line1}\n{line2}\n{line3}"
            
            sys_instruct = (
                "You are an expert e-commerce catalog copywriter for authentic Indian artisans and handicrafts. "
                "Transform the artisan's informal spoken input into a rich, customer-ready 3-line product description in English: "
                "Line 1 covers the craft identity, cultural heritage, and historical origin. "
                "Line 2 covers material authenticity, purity, and traditional handcrafting artistry. "
                "Line 3 covers utility, comfort, aesthetic appeal, and intrinsic artisanal value. "
                "Do NOT include prices. Output exactly 3 cohesive, polished sentences in English without extra commentary."
            )

            samples.append({
                "id": f"hero_desc_{sample_id:04d}",
                "craft_id": craft["id"],
                "craft_name": craft["name"],
                "category": craft["category"],
                "region": craft["region"],
                "raw_speech_input": raw_input,
                "line1_history_heritage": line1,
                "line2_originality_material": line2,
                "line3_utility_value": line3,
                "full_3line_description": full_description,
                "messages": [
                    {"role": "system", "content": sys_instruct},
                    {"role": "user", "content": raw_input},
                    {"role": "assistant", "content": full_description}
                ],
                "instruction": sys_instruct,
                "input": raw_input,
                "output": full_description
            })
            sample_id += 1

    # Shuffle to mix crafts
    random.shuffle(samples)

    # Export to CSV
    csv_path = "e:/Harsh/VIT/Hackathons/SIH 2026/Speech Translation/datasets/artisan_rich_descriptions.csv"
    fieldnames = [
        "id", "craft_id", "craft_name", "category", "region", 
        "raw_speech_input", "line1_history_heritage", 
        "line2_originality_material", "line3_utility_value", "full_3line_description"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for s in samples:
            writer.writerow(s)

    # Export to JSONL
    jsonl_path = "e:/Harsh/VIT/Hackathons/SIH 2026/Speech Translation/datasets/artisan_rich_descriptions.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for s in samples:
            # For JSONL we only need the ChatML format for fine-tuning
            f.write(json.dumps({
                "messages": s["messages"]
            }, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    generate_hero_dataset()
