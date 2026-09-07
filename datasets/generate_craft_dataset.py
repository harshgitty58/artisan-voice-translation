"""
generate_craft_dataset.py
-------------------------
Generates an authentic, rich multi-lingual dataset for training / fine-tuning
Qwen2.5 and other LLMs for Indian Artisan Product Cataloging.

Each entry pairs a terse, informal raw speech input (in English, Hindi, or Marathi)
with a rich 3-line storytelling e-commerce description featuring:
  Line 1: Craft Identity & Cultural Heritage (origin, 2-word/century history, royal patronage)
  Line 2: Authenticity & Material Originality (100% pure materials, traditional hand-crafting)
  Line 3: Utility, Everyday/Festive Appeal & Value (durability, comfort, price context)
"""

import json
import csv
import os
import random
from typing import List, Dict

CRAFT_KNOWLEDGE = [
    {
        "craft_id": "kolhapuri_chappal",
        "name": "Kolhapuri Leather Chappals",
        "category": "Footwear",
        "region": "Kolhapur, Maharashtra / Karnataka",
        "history_heritage": "Dating back to the 12th century under the royal patronage of the Shilahara dynasty and later championed by Chhatrapati Shahu Maharaj, authentic Kolhapuri chappals are a celebrated icon of Maratha footwear heritage.",
        "originality_materials": "Meticulously handcrafted from 100% pure vegetable-tanned leather treated with natural babool bark extracts, each pair features intricate hand-braided straps assembled with zero metal nails.",
        "utility_value": "Engineered for breathable comfort and remarkable durability, these artisanal chappals soften naturally to the contours of your feet, offering timeless ethnic elegance for festive wear and daily use.",
        "price_range": (850, 1800),
        "speech_inputs": {
            "en": [
                "kolhapuri chappal, pure leather, {price} rs.",
                "Handmade Kolhapuri sandals, genuine leather, {price} rupees, traditional style.",
                "This is pure leather kolhapuri chappal, handcrafted in Kolhapur, {price} rs only.",
                "um... original kolhapuri chappal, brown leather, hand braided, price is {price}.",
                "Authentic leather footwear, Kolhapuri pattern, {price} rupees, very durable."
            ],
            "hi": [
                "कोल्हापुरी चप्पल, शुद्ध चमड़ा, {price} रुपये।",
                "यह हाथ से बनी कोल्हापुरी चप्पल है, असली लेदर, कीमत {price} रु।",
                "शुद्ध चमड़े की पारंपरिक कोल्हापुरी चप्पल, हाथ की सिलाई, {price} रुपये।",
                "कोल्हापुर की असली लेदर चप्पल, बहुत मजबूत, {price} में।",
                "हाथ से बना कोल्हापुरी सैंडल, असली चमड़ा, {price} रुपये।"
            ],
            "mr": [
                "कोल्हापुरी चप्पल, अस्सल चामडे, {price} रुपये.",
                "हे हाताने बनवलेले कोल्हापुरी चप्पल आहे, अस्सल लेदर, किंमत {price} रुपये.",
                "कोल्हापूरची पारंपरिक चप्पल, शुद्ध चामड्याची, {price} रुपये.",
                "अस्सल कोल्हापुरी पायताण, हातविणकाम, {price} रुपयांत.",
                "हे चामड्याचे कोल्हापुरी चप्पल, खूप टिकाऊ, किंमत {price}."
            ]
        }
    },
    {
        "craft_id": "chanderi_saree",
        "name": "Handloom Chanderi Silk Saree",
        "category": "Textiles & Handlooms",
        "region": "Chanderi, Ashoknagar, Madhya Pradesh",
        "history_heritage": "Dating back to the Vedic era and flourishing under 14th-century Bundela royal patronage in central India, Chanderi weaving is one of India's most revered handloom traditions.",
        "originality_materials": "Woven on traditional pit looms blending pure Mulberry silk warp with fine combed cotton, adorned with authentic gold zari floral bootis and an ornate pallu.",
        "utility_value": "Celebrated for its feather-light gossamer drape, subtle natural shimmer, and soft tactile feel, it provides majestic elegance for festive ceremonies, poojas, and weddings.",
        "price_range": (2400, 5500),
        "speech_inputs": {
            "en": [
                "This is a handloom chanderi silk saree with gold zari border, {price} rupees, traditional weave.",
                "Chanderi saree, pure silk cotton, zari booti, {price} rs.",
                "Handcrafted chanderi silk sari from MP, golden border, {price} rupees.",
                "Handloom chanderi saree, lightweight silk, price {price}.",
                "pure chanderi silk saree with traditional weave, {price} rupees."
            ],
            "hi": [
                "यह हथकरघा चंदेरी सिल्क साड़ी है, जरी बॉर्डर के साथ, {price} रुपये, पारंपरिक बुनाई।",
                "चंदेरी साड़ी, शुद्ध रेशम और सूती, सुनहरी जरी, {price} रु।",
                "मध्य प्रदेश की प्रसिद्ध चंदेरी सिल्क साड़ी, हाथ से बुनी हुई, कीमत {price} रुपये।",
                "चंदेरी हाथ की बुनी साड़ी, हल्की रेशमी, {price} में।",
                "शुद्ध चंदेरी जरी साड़ी, पूजा और त्योहार के लिए, {price} रुपये।"
            ],
            "mr": [
                "ही हातमागावर विणलेली चंदेरी रेशमी साडी आहे, जरी काठ, {price} रुपये.",
                "चंदेरी साडी, अस्सल सिल्क कॉटन, सोन्याची जरी, {price} रुपये.",
                "हातमागाची पारंपरिक चंदेरी साडी, हलकी आणि मऊ, किंमत {price}.",
                "मध्य प्रदेशातील प्रसिद्ध चंदेरी रेशीम साडी, {price} रुपये.",
                "पारंपरिक चंदेरी साडी, सणावारासाठी उत्तम, {price} रुपयांत."
            ]
        }
    },
    {
        "craft_id": "paithani_saree",
        "name": "Traditional Yeola Paithani Silk Saree",
        "category": "Textiles & Handlooms",
        "region": "Yeola / Paithan, Maharashtra",
        "history_heritage": "Originating over 2,000 years ago during the ancient Satavahana dynasty and later cherished as royal regalia by the Peshwas, the Paithani saree is revered as the 'Queen of Indian Silks'.",
        "originality_materials": "Meticulously handwoven on wooden tapestries from 100% pure filature silk, showcasing certified pure silver-gold zari with signature hand-interlocked peacock (mor) and parrot motifs.",
        "utility_value": "Characterized by its radiant kaleidoscopic dual-tone luster and generational heirloom longevity, this masterpiece embodies auspicious prosperity for weddings and festive milestones.",
        "price_range": (6500, 18000),
        "speech_inputs": {
            "en": [
                "Yeola Paithani saree, pure silk with peacock pallu, {price} rupees.",
                "Traditional Maharashtrian Paithani, handwoven silk, zari border, {price} rs.",
                "This is a bridal Paithani silk saree, mor butti, {price} rupees.",
                "Pure handloom paithani saree, authentic yeola weave, price {price}.",
                "Authentic silk paithani with gold zari pallu, {price} rupees."
            ],
            "hi": [
                "यह येवला पैठणी सिल्क साड़ी है, मोर पल्लू के साथ, शुद्ध रेशम, {price} रुपये।",
                "पारंपरिक पैठणी साड़ी, हाथ से बुनी रेशमी, सुनहरी जरी, {price} रु।",
                "महाराष्ट्र की प्रसिद्ध पैठणी रेशम साड़ी, मोर बूटी, कीमत {price} रुपये।",
                "शुद्ध सिल्क पैठणी साड़ी, शादी-ब्याह के लिए, {price} रुपये।",
                "हथकरघा पैठणी साड़ी, असली जरी का काम, {price} रुपये।"
            ],
            "mr": [
                "ही येवला पैठणी साडी आहे, मोर पल्लू, अस्सल रेशीम, {price} रुपये.",
                "पारंपरिक महाराष्ट्रीयन पैठणी साडी, हातमाग रेशीम, जरी काठ, {price} रुपये.",
                "अस्सल येवला पैठणी, सोन्याच्या जरीची नक्षी, किंमत {price} रुपये.",
                "लग्नासाठी खास पैठणी साडी, पोपट-मोर पदर, {price} रुपये.",
                "हातमागावर विणलेली अस्सल पैठणी, {price} रुपयांत."
            ]
        }
    },
    {
        "craft_id": "banarasi_saree",
        "name": "Handwoven Banarasi Brocade Silk Saree",
        "category": "Textiles & Handlooms",
        "region": "Varanasi, Uttar Pradesh",
        "history_heritage": "Celebrated since the Mahabharata and Mughal era in the ancient holy city of Varanasi, Banarasi weaving represents India's pinnacle imperial textile craft.",
        "originality_materials": "Handcrafted on historic pit looms using 100% pure Katan Mulberry silk, intricately brocaded with genuine gold and silver zari forming ornate floral jaal (foliage) and paisley patterns.",
        "utility_value": "Renowned for its heavy royal drape, opulent metallic sheen, and lasting prestige, it remains the ultimate bridal treasure handed down as a family heirloom.",
        "price_range": (4500, 15000),
        "speech_inputs": {
            "en": [
                "Handwoven Banarasi silk saree, red and gold zari brocade, {price} rupees.",
                "Varanasi katan silk saree, authentic zari work, {price} rs.",
                "Banarasi bridal saree, pure silk, handloom woven, {price} rupees.",
                "Traditional Banarasi brocade saree, floral jaal, price {price}.",
                "Original Varanasi silk saree, heavy zari pallu, {price} rupees."
            ],
            "hi": [
                "बनारसी सिल्क साड़ी, लाल और सुनहरा जरी ब्रोकेड, हाथ से बुनी, {price} रुपये।",
                "वाराणसी की शुद्ध कातान सिल्क साड़ी, असली जरी का काम, {price} रु।",
                "बनारसी दुल्हन साड़ी, हथकरघा रेशम, कीमत {price} रुपये।",
                "पारंपरिक बनारसी साड़ी, फूलों का जाल, {price} में।",
                "शुद्ध बनारसी जरी साड़ी, भारी पल्लू, {price} रुपये।"
            ],
            "mr": [
                "बनारसी सिल्क साडी, लाल आणि सोनेरी जरीचे नक्षीकाम, {price} रुपये.",
                "वाराणसीची अस्सल कातान सिल्क साडी, हातमाग बुनावट, {price} रुपये.",
                "पारंपरिक बनारसी ब्रोकेड साडी, सोन्याची जरी, किंमत {price}.",
                "शुद्ध रेशमी बनारसी साडी, लग्नसराईसाठी, {price} रुपये.",
                "हातमागावर तयार केलेली बनारसी साडी, {price} रुपयांत."
            ]
        }
    },
    {
        "craft_id": "brass_peacock_diya",
        "name": "Handcrafted Pure Brass Peacock Diya",
        "category": "Metal & Brassware",
        "region": "Moradabad, Uttar Pradesh",
        "history_heritage": "Rooted in sacred Vedic pooja customs and centuries of artisanal metal-casting traditions in Moradabad—India's historic 'Brass City'—the peacock diya embodies cultural devotion.",
        "originality_materials": "Solid cast from 100% virgin bell-brass using age-old sand-casting methods, individually chiseled and polished by master thatheras with an auspicious peacock crest.",
        "utility_value": "Designed for daily spiritual aarti, Diwali festivities, and heirloom home aesthetics, its radiant golden surface resists oxidation and delivers a warm, divine ambient glow.",
        "price_range": (650, 2200),
        "speech_inputs": {
            "en": [
                "Handmade brass peacock diya, for pooja and aarti, {price} rs, pure brass.",
                "Traditional brass oil lamp with peacock design, heavy quality, {price} rupees.",
                "This is a brass samai lamp, engraved peacock, {price} rupees.",
                "Solid brass diya for festive home decor, price {price} rs.",
                "Pure brass decorative diya, handmade in Moradabad, {price} rupees."
            ],
            "hi": [
                "यह हाथ से बना पीतल का मयूर दीया है, पूजा और आरती के लिए, {price} रुपये, शुद्ध पीतल।",
                "पीतल का पारंपरिक दीया, मोर की नक्काशी, भारी वजन, {price} रु।",
                "मुरादाबाद का हस्तनिर्मित पीतल दीया, शुद्ध ब्रास, कीमत {price} रुपये।",
                "पीतल की समयी, मंदिर और सजावट के लिए, {price} रुपये में।",
                "शुद्ध पीतल का मयूर दीपक, हाथ से ढला हुआ, {price} रुपये।"
            ],
            "mr": [
                "हे हातांनी बनवलेले पितळेचे मयूर दिवा आहे, पूजेसाठी, {price} रुपये, शुद्ध पितळ.",
                "पितळेची पारंपरिक समई, मोर नक्षीकाम, वजनदार, किंमत {price} रुपये.",
                "हाताने तयार केलेला पितळेचा दिवा, घर सजावटीसाठी, {price} रुपये.",
                "शुद्ध पितळी मयूर दीप, देवघरासाठी, {price} रुपयांत.",
                "पितळेचा नक्षीदार दिवा, मजबूत आणि टिकाऊ, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "jaipur_blue_pottery",
        "name": "Jaipur Hand-Painted Blue Pottery Vase",
        "category": "Pottery & Ceramics",
        "region": "Jaipur, Rajasthan",
        "history_heritage": "Patronized in the 19th century by Sawai Ram Singh II and rooted in Turko-Persian traditions, Jaipur Blue Pottery is a globally acclaimed GI-tagged craft of Rajasthan.",
        "originality_materials": "Uniquely made without traditional clay using a heritage composite of ground quartz stone, Fuller's earth, and natural gum, hand-painted with cobalt oxide and copper pigments.",
        "utility_value": "Impervious to water with a high-gloss crackle-free glaze, this striking artistic vase infuses desert royal charm into contemporary dining tables, consoles, and mantelpieces.",
        "price_range": (550, 1900),
        "speech_inputs": {
            "en": [
                "Jaipur blue pottery flower vase, hand painted floral pattern, {price} rs.",
                "Traditional blue pottery ceramic pot, blue and turquoise, {price} rupees.",
                "Handcrafted Rajasthani blue pottery vase, quartz stone, {price} rs.",
                "Blue pottery decorative pot from Jaipur, price {price} rupees.",
                "Floral painted blue pottery urn, handmade craft, {price} rs."
            ],
            "hi": [
                "जयपुर ब्लू पॉटरी फूलदान, हाथ से बनी फूलों की डिजाइन, {price} रुपये।",
                "पारंपरिक ब्लू पॉटरी मिट्टी का बर्तन नहीं, क्वार्ट्ज से बना, {price} रु।",
                "राजस्थान की हस्तनिर्मित ब्लू पॉटरी, नीले और फिरोजी रंग, कीमत {price} रुपये।",
                "हस्तशिल्प ब्लू पॉटरी फूलदान, सजावट के लिए, {price} में।",
                "जयपुर का प्रसिद्ध ब्लू पॉटरी सुराही, हाथ की कारीगरी, {price} रुपये।"
            ],
            "mr": [
                "जयपूर ब्लू पॉटरी फुलदाणी, हातांनी रंगवलेली फुलांची नक्षी, {price} रुपये.",
                "पारंपरिक राजस्थानी ब्लू पॉटरी, सुंदर निळा रंग, किंमत {price} रुपये.",
                "हाताने बनवलेले ब्लू पॉटरी भांडे, सजावटीसाठी, {price} रुपये.",
                "जयपूरची प्रसिद्ध ब्लू पॉटरी कलाकृती, {price} रुपयांत.",
                "क्वाॉर्ट्झपासून बनवलेली आकर्षक ब्लू पॉटरी, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "bastar_dhokra",
        "name": "Bastar Tribal Dhokra Bell Metal Figurine",
        "category": "Metal Crafts",
        "region": "Bastar, Chhattisgarh / Bankura, West Bengal",
        "history_heritage": "Continuing a continuous 4,000-year metallurgical legacy directly linked to the prehistoric Mohenjo-daro Dancing Girl, Dhokra is preserved by indigenous Ghadwa tribal clans.",
        "originality_materials": "Masterfully formed using the ancient lost-wax casting technique (cire perdue) with wild bees' wax and recycled brass-bronze alloy, making each sculpture a completely unique one-of-a-kind original.",
        "utility_value": "Featuring captivating primitive folk motifs of musicians, tribal deities, and wildlife, this rustic artifact stands as a museum-caliber centerpiece for discerning collectors.",
        "price_range": (900, 3500),
        "speech_inputs": {
            "en": [
                "Dhokra bell metal tribal figurine, lost wax casting, {price} rupees.",
                "Handcrafted tribal brass craft from Bastar, musician idol, {price} rs.",
                "Authentic Dhokra art piece, antique brass finish, {price} rupees.",
                "Lost wax cast brass tribal artifact, Bastar dokra, price {price}.",
                "Traditional Dhokra horse figurine, handmade bell metal, {price} rupees."
            ],
            "hi": [
                "बस्तर ढोकरा मेटल आदिवासी मूर्ति, मोम ढलाई तकनीक, {price} रुपये।",
                "हस्तनिर्मित बस्तर ब्रास शिल्प, आदिवासी नर्तक, {price} रु।",
                "पारंपरिक ढोकरा धातु कलाकृति, पीतल और कांस्य, कीमत {price} रुपये।",
                "4000 साल पुरानी तकनीक से बनी ढोकरा मूर्ति, {price} रुपये।",
                "शुद्ध बेल मेटल ढोकरा हस्तशिल्प, {price} में।"
            ],
            "mr": [
                "बस्तर ढोकरा मेटल आदिवासी मूर्ती, प्राचीन मेण ओतकाम, {price} रुपये.",
                "हाताने बनवलेली ढोकरा पितळ कलाकृती, संगीतकार मूर्ती, {price} रुपये.",
                "पारंपरिक ढोकरा धातू शिल्प, वैशिष्ट्यपूर्ण रचना, किंमत {price}.",
                "बस्तरची प्रसिद्ध ढोकरा कला, अस्सल हस्तकला, {price} रुपयांत.",
                "आदिवासी हस्तनिर्मित ब्रास मूर्ती, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "madhubani_painting",
        "name": "Authentic Madhubani Hand-Painted Canvas Art",
        "category": "Paintings & Folk Art",
        "region": "Mithila / Madhubani, Bihar",
        "history_heritage": "Originating in the Mithila region during the Treta Yuga when King Janaka commissioned wall murals for Princess Sita's wedding, Madhubani is one of India's most sacred folk art forms.",
        "originality_materials": "Freehand painted by village women artisans using natural bamboo twigs and fine nibs, utilizing vibrant organic pigments extracted from marigold, indigo, soot, and turmeric.",
        "utility_value": "Adorned with intricate geometric borders and auspicious nature motifs like the Tree of Life and fish, it infuses living rooms and gallery walls with cultural serenity and warmth.",
        "price_range": (800, 4200),
        "speech_inputs": {
            "en": [
                "Madhubani painting on handmade paper, tree of life, {price} rupees.",
                "Mithila folk art painting, natural colors, handmade, {price} rs.",
                "Hand-painted Madhubani wall decor, fish and peacock motif, {price} rupees.",
                "Original Madhubani artwork, organic vegetable dyes, price {price}.",
                "Traditional Bihar folk painting, framed wall art, {price} rs."
            ],
            "hi": [
                "मधुबनी पेंटिंग हस्तनिर्मित कागज पर, जीवन का पेड़, {price} रुपये।",
                "मिथिला लोक कला पेंटिंग, प्राकृतिक रंगों से बनी, {price} रु।",
                "हाथ से चित्रित मधुबनी वॉल आर्ट, मछली और मयूर, कीमत {price} रुपये।",
                "शुद्ध जैविक रंगों से बनी मधुबनी कलाकृति, {price} में।",
                "बिहार की पारंपरिक मधुबनी पेंटिंग, हाथ की नक्काशी, {price} रुपये।"
            ],
            "mr": [
                "मधुबनी चित्रकला हाताने बनवलेल्या कागदावर, नैसर्गिक रंग, {price} रुपये.",
                "मिथिला लोककला चित्र, झाड आणि मोर नक्षी, किंमत {price} रुपये.",
                "हातांनी रंगवलेली अस्सल मधुबनी वॉल आर्ट, {price} रुपयांत.",
                "पारंपरिक भारतीय लोकचित्रकला, मधुबनी फ्रेम, {price} रुपये.",
                "सेंद्रिय रंगांनी रेखाटलेली मधुबनी कला, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "warli_art",
        "name": "Traditional Warli Tribal Wall Art Decor",
        "category": "Paintings & Folk Art",
        "region": "North Sahyadri, Palghar / Dahanu, Maharashtra",
        "history_heritage": "Rooted in prehistoric rock shelter art dating back to 2500 BCE in Maharashtra's Sahyadri ranges, Warli art celebrates the organic equilibrium between tribal life, nature, and mother earth.",
        "originality_materials": "Rendered using minimalist prehistoric geometry of circles, triangles, and squares, hand-brushed with pure white rice paste and gum onto an earthen terracotta-toned canvas.",
        "utility_value": "Capturing rhythmic spiral tarpa dances and rural harvest celebrations, this monochromatic folk art brings soulful indigenous warmth and earthy sophistication to modern interiors.",
        "price_range": (600, 2600),
        "speech_inputs": {
            "en": [
                "Warli tribal painting on canvas, tarpa dance, {price} rupees.",
                "Handmade Warli wall decor, traditional Maharashtra art, {price} rs.",
                "Authentic Warli art frame, white rice paste painting, {price} rupees.",
                "Tribal Warli folk painting, harvest celebration, price {price}.",
                "Maharashtra Warli art piece, earth tone canvas, {price} rs."
            ],
            "hi": [
                "वारली आदिवासी पेंटिंग कैनवास पर, तारपा नृत्य, {price} रुपये।",
                "हाथ से बनी वारली वॉल आर्ट, पारंपरिक महाराष्ट्र लोककला, {price} रु।",
                "चावल के लेप से बनी प्रामाणिक वारली कलाकृति, कीमत {price} रुपये।",
                "वारली जनजातीय चित्रकला, प्राकृतिक मिट्टी के रंग, {price} में।",
                "पारंपरिक वारली फ्रेम, ग्रामीण जीवन का दृश्य, {price} रुपये।"
            ],
            "mr": [
                "वारली आदिवासी चित्रकला कॅनव्हासवर, तारपा नृत्य, {price} रुपये.",
                "हाताने रंगवलेली वारली कला, महाराष्ट्राची लोकसंस्कृती, किंमत {price} रुपये.",
                "तांदळाच्या पिठाने रेखाटलेली अस्सल वारली पेंटिंग, {price} रुपयांत.",
                "पारंपरिक सह्याद्री वारली हस्तकला, {price} रुपये.",
                "वारली लोकचित्रकला फ्रेम, घर सजावटीसाठी, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "kashmiri_pashmina",
        "name": "Pure Handwoven Kashmiri Pashmina Shawl",
        "category": "Textiles & Woollens",
        "region": "Srinagar, Jammu & Kashmir",
        "history_heritage": "Patronized by Mughal emperors and European monarchs since the 15th-century reign of Sultan Zain-ul-Abidin, Kashmiri Pashmina stands as the undisputed summit of textile luxury.",
        "originality_materials": "Hand-spun from rare, ultra-fine underfleece combed from Changthangi mountain goats in Ladakh, handwoven on traditional wooden looms with delicate sozni needlework.",
        "utility_value": "Incomparably feather-light, cloud-soft, and exceptionally insulating, this heritage wrap drapes with regal grace to elevate evening ensembles through chilly seasons for decades.",
        "price_range": (5500, 22000),
        "speech_inputs": {
            "en": [
                "Pure Kashmiri Pashmina shawl, handwoven, cream color, {price} rupees.",
                "Authentic Cashmere pashmina wrap, sozni hand embroidery, {price} rs.",
                "Handmade pashmina wool shawl from Srinagar, {price} rupees.",
                "100% pure pashmina shawl, feather light warmth, price {price}.",
                "Luxury Kashmiri pashmina stole, needlework border, {price} rs."
            ],
            "hi": [
                "शुद्ध कश्मीरी पश्मीना शॉल, हाथ से बुनी, क्रीम रंग, {price} रुपये।",
                "असली कश्मीरी पश्मीना रैप, सोजनी हाथ की कढ़ाई, {price} रु।",
                "श्रीनगर का हस्तनिर्मित पश्मीना शॉल, बहुत हल्का और गर्म, कीमत {price} रुपये।",
                "100% शुद्ध पश्मीना ऊन, राजसी शान, {price} रुपये में।",
                "पारंपरिक कश्मीरी पश्मीना स्टोल, हाथ का काम, {price} रुपये।"
            ],
            "mr": [
                "शुद्ध काश्मिरी पश्मिना शाल, हातमाग विणकाम, {price} रुपये.",
                "अस्सल काश्मिरी पश्मिना, हाताने केलेली भरतकाम, किंमत {price} रुपये.",
                "श्रीनगरची प्रसिद्ध पश्मिना शाल, मऊ आणि उबदार, {price} रुपयांत.",
                "१००% शुद्ध पश्मिना लोकर, शाही वैभव, {price} रुपये.",
                "काश्मिरी पश्मिना स्टोल, आकर्षक नक्षीकाम, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "bidriware_box",
        "name": "Handcrafted Bidriware Pure Silver Inlay Box",
        "category": "Metal & Jewelry",
        "region": "Bidar, Karnataka",
        "history_heritage": "Originating in the 14th century during the reign of the Bahmani Sultans in Bidar, Bidriware is a globally celebrated GI craft known for its dramatic contrast between silver and velvet black.",
        "originality_materials": "Cast from a specialized non-ferrous zinc-copper alloy, deeply hand-etched with geometric arabesques, inlaid with sheets of certified 99.9% pure silver, and blackened with historic Bidar fort mud.",
        "utility_value": "Permanently tarnish-resistant with an arresting matte black luster, this royal utility keepsake serves as an opulent trinket box or distinguished executive desk heirloom.",
        "price_range": (1200, 4800),
        "speech_inputs": {
            "en": [
                "Bidriware silver inlay jewelry box, black metal, {price} rupees.",
                "Handmade Bidri craft keepsake, pure silver wire inlay, {price} rs.",
                "Authentic Bidar metalwork box, geometric floral pattern, {price} rupees.",
                "Traditional Bidriware box from Karnataka, price {price} rs.",
                "Pure silver inlay Bidri artifact, matte black finish, {price} rupees."
            ],
            "hi": [
                "बिदरीवेयर चांदी की नक्काशी वाला बॉक्स, काला मेटल, {price} रुपये।",
                "हाथ से बना बिदरी शिल्प, शुद्ध चांदी का तार इनले, {price} रु।",
                "बीदर का प्रसिद्ध मेटलवर्क डिब्बा, शाही नक्काशी, कीमत {price} रुपये।",
                "कर्नाटक का पारंपरिक बिदरीवेयर हैंडीक्राफ्ट, {price} में।",
                "शुद्ध चांदी जड़ित बिदरी कलाकृति, {price} रुपये।"
            ],
            "mr": [
                "बिदरीवेअर चांदीचे नक्षीकाम असलेला डबा, काळा धातू, {price} रुपये.",
                "हाताने तयार केलेले बिदरी हस्तशिल्प, शुद्ध चांदीचे इनले, {price} रुपये.",
                "कर्नाटकातील बिदरची प्रसिद्ध धातुकला, किंमत {price} रुपये.",
                "पारंपरिक बिदरी कलाकृती, शाही भेटवस्तू, {price} रुपयांत.",
                "अस्सल बिदरी धातू पेटी, सुंदर कोरीवकाम, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "channapatna_toys",
        "name": "Channapatna Wooden Handcrafted Toy Set",
        "category": "Woodcraft & Toys",
        "region": "Channapatna, Ramanagara, Karnataka",
        "history_heritage": "Introduced in the late 18th century under the royal patronage of Tipu Sultan who invited Persian artisans, Channapatna's 'Gombegala Ooru' (Toy Town) is a UNESCO-recognized toycraft capital.",
        "originality_materials": "Turned on traditional wood lathes from sustainably harvested Wrightia tinctoria (Aale mara / Ivory wood), finished using 100% natural, child-safe vegetable lac and turmeric dyes.",
        "utility_value": "Completely splinter-free with smooth rounded contours and vibrant non-toxic finishes, these eco-conscious toys cultivate motor skills while serving as nostalgic retro decor.",
        "price_range": (450, 1600),
        "speech_inputs": {
            "en": [
                "Channapatna wooden toy stacker, vegetable lac colors, safe for kids, {price} rs.",
                "Handcrafted wooden rocking horse from Channapatna, {price} rupees.",
                "Traditional Karnataka wooden toy set, eco friendly, {price} rs.",
                "Non toxic wooden educational toy, Channapatna craft, price {price}.",
                "Hand turned ivory wood toys, natural lacquer finish, {price} rupees."
            ],
            "hi": [
                "चन्नापट्टना लकड़ी का खिलौना, प्राकृतिक लाख के रंग, बच्चों के लिए सुरक्षित, {price} रुपये।",
                "हाथ से बने पारंपरिक लकड़ी के खिलौने, टीपू सुल्तान का शिल्प, {price} रु।",
                "कर्नाटक के पर्यावरण-अनुकूल लकड़ी के खिलौने, कीमत {price} रुपये।",
                "विषरहित प्राकृतिक रंगों वाले चन्नापट्टना खिलौने, {price} में।",
                "हस्तनिर्मित चन्नापट्टना वुडन टॉय सेट, {price} रुपये।"
            ],
            "mr": [
                "चन्नापट्टणा लाकडी खेळणी संच, नैसर्गिक रंगांचे कोटिंग, मुलांसाठी सुरक्षित, {price} रुपये.",
                "हाताने कोरलेली लाकडी खेळणी, चन्नापट्टणा कला, किंमत {price} रुपये.",
                "पर्यावरणपूरक लाकडी खेळणी, बिनविषारी भाज्यांचे रंग, {price} रुपयांत.",
                "कर्नाटकातील ऐतिहासिक चन्नापट्टणा खेळणी, {price} रुपये.",
                "पारंपरिक लाकडी खेळण्यांचा सेट, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "terracotta_pot",
        "name": "Gorakhpur Hand-Burnished Terracotta Clay Pot",
        "category": "Pottery & Clay",
        "region": "Gorakhpur, Uttar Pradesh",
        "history_heritage": "Descending from millennia-old Gangetic clay potting guilds and honored with a dedicated GI tag, Gorakhpur terracotta represents India's living earthenware heritage.",
        "originality_materials": "Wheel-thrown from nutrient-dense local alluvial clay, intricately carved with floral jaali cutwork, and wood-fired to achieve its signature rich terracotta red patina.",
        "utility_value": "Naturally porous and eco-friendly, it provides exceptional natural evaporative cooling for water, promotes plant vitality, and radiates rustic earthy warmth.",
        "price_range": (350, 1400),
        "speech_inputs": {
            "en": [
                "Terracotta clay pot, hand painted floral pattern, {price} rupees.",
                "Handmade earthen clay pot, natural terracotta, for plants and decor, {price} rs.",
                "Gorakhpur terracotta vase, traditional cutwork, {price} rupees.",
                "Eco friendly terracotta planter pot, natural clay, price {price}.",
                "Handcrafted clay matka pot, cooling earthenware, {price} rs."
            ],
            "hi": [
                "टेराकोटा मिट्टी का गमला, हाथ से बना फूलों का पैटर्न, {price} रुपये।",
                "हाथ से बना प्राकृतिक मिट्टी का घड़ा, सजावट और पौधों के लिए, {price} रु।",
                "गोरखपुर टेराकोटा फूलदान, पारंपरिक नक्काशी, कीमत {price} रुपये।",
                "पर्यावरण अनुकूल मिट्टी का बर्तन, प्राकृतिक टेराकोटा, {price} में।",
                "हस्तनिर्मित मिट्टी का खूबसूरत मटका, {price} रुपये।"
            ],
            "mr": [
                "टेराकोटा मातीचे भांडे, हातांनी रंगवलेले, {price} रुपये.",
                "हाताने बनवलेली मातीची कुंडी, घर आणि बागेच्या सजावटीसाठी, {price} रुपये.",
                "पारंपरिक टेराकोटा मातीचे मडके, नैसर्गिक थंडपणा, किंमत {price}.",
                "पर्यावरणपूरक मातीची भांडी, अस्सल कारागिरी, {price} रुपयांत.",
                "हस्तनिर्मित टेराकोटा शोपीस, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "jute_tote_bag",
        "name": "Artisanal Eco-Friendly Handcrafted Jute Tote Bag",
        "category": "Eco-Crafts & Natural Fibers",
        "region": "Bengal Delta / Odisha",
        "history_heritage": "Anchored in the fertile Ganges-Brahmaputra delta known worldwide as the heartland of India's 'Golden Fiber', jute weaving has championed eco-conscious sustainable livelihoods for centuries.",
        "originality_materials": "Woven from 100% unbleached organic golden jute fiber paired with vegetable-dyed cotton trims, reinforced cross-stitched handles, and zero synthetic plastic lamination.",
        "utility_value": "Highly resilient with a generous multi-pocket capacity of up to 15 kg, this breathable biodegradable tote offers a sophisticated, planet-positive staple for daily errands and markets.",
        "price_range": (350, 950),
        "speech_inputs": {
            "en": [
                "This is a jute bag, very sturdy, good for daily use, {price} rs.",
                "Handcrafted eco friendly jute tote bag, cotton handle, {price} rupees.",
                "Natural golden jute shopping bag, reusable, price {price} rs.",
                "Handmade jute handbag with zipper, ethnic print, {price} rupees.",
                "Sturdy organic jute shoulder bag, {price} rupees."
            ],
            "hi": [
                "यह जूट का थैला है, बहुत मजबूत, रोज के इस्तेमाल के लिए, {price} रुपये।",
                "हाथ से बना पर्यावरण-अनुकूल जूट टोट बैग, कॉटन हैंडल, {price} रु।",
                "प्राकृतिक गोल्डन जूट शॉपिंग बैग, पुन: प्रयोज्य, कीमत {price} रुपये।",
                "हस्तनिर्मित जूट बैग, चेन के साथ, {price} में।",
                "मजबूत जैविक जूट थैला, प्लास्टिक मुक्त, {price} रुपये।"
            ],
            "mr": [
                "ही तागाची पिशवी आहे, खूप मजबूत, रोजच्या वापरासाठी, {price} रुपये.",
                "हातांनी विणलेली पर्यावरणपूरक जूट पिशवी, सुती हँडल, {price} रुपये.",
                "अस्सल जूट शॉपिंग बॅग, टिकाऊ आणि सुंदर, किंमत {price}.",
                "प्लॅस्टिकमुक्त नैसर्गिक जूट पिशवी, {price} रुपयांत.",
                "मजबूत हातनिर्मित तागाची बॅग, {price} रुपये."
            ]
        }
    },
    {
        "craft_id": "sheesham_wood_box",
        "name": "Hand-Carved Sheesham Wood Keepsake Box",
        "category": "Woodcraft",
        "region": "Saharanpur, Uttar Pradesh",
        "history_heritage": "Reflecting the majestic floral fretwork of Mughal architectural monuments, Saharanpur's generational woodcarvers have sustained northern India's premier timber handicraft for over 400 years.",
        "originality_materials": "Hand-chiseled from legally harvested, well-seasoned Indian Sheesham (Dalbergia sissoo) rosewood, adorned with brass filigree inlays and buffed with natural beeswax without artificial varnish.",
        "utility_value": "Naturally termite-resistant with a velvet-lined interior and antique brass latch, it keeps precious jewelry, heirlooms, and watches impeccably protected in timeless grandeur.",
        "price_range": (650, 2400),
        "speech_inputs": {
            "en": [
                "Wooden carved jewelry box, dark brown finish, {price} rupees.",
                "Handcrafted sheesham wood box with brass inlay, {price} rs.",
                "Saharanpur hand carved wooden keepsake chest, {price} rupees.",
                "Solid rosewood decorative box, floral carving, price {price}.",
                "Traditional carved wooden box for valuables, {price} rs."
            ],
            "hi": [
                "लकड़ी का नक्काशीदार आभूषण बॉक्स, गहरा भूरा फिनिश, {price} रुपये।",
                "शीशम की लकड़ी का हस्तनिर्मित डिब्बा, पीतल की नक्काशी, {price} रु।",
                "सहारनपुर की प्रसिद्ध लकड़ी की पेटी, हाथ से तराशी हुई, कीमत {price} रुपये।",
                "सॉलिड शीशम वुड जेवर बॉक्स, मजबूत और सुंदर, {price} में।",
                "पारंपरिक हाथ से नक्काशी किया हुआ लकड़ी का बक्सा, {price} रुपये।"
            ],
            "mr": [
                "लाकडी नक्षीकाम केलेली पेटी, गडद तपकिरी रंग, {price} रुपये.",
                "शीशमच्या लाकडाचा हाताने बनवलेला दागिन्यांचा डबा, {price} रुपये.",
                "सहारनपूरची प्रसिद्ध लाकडी पेटी, बारीक कोरीवकाम, किंमत {price}.",
                "अस्सल लाकडी शोभेची पेटी, पितळी नक्षी, {price} रुपयांत.",
                "हातांनी कोरलेली पारंपरिक लाकडी पेटी, {price} रुपये."
            ]
        }
    }
]


def generate_full_dataset(num_variations_per_craft: int = 15) -> List[Dict]:
    """
    Generates a full dataset of prompt-completion pairs covering English, Hindi,
    and Marathi informal inputs mapped to rich 3-line e-commerce descriptions.
    """
    samples = []
    sample_id = 1

    for craft in CRAFT_KNOWLEDGE:
        p_min, p_max = craft["price_range"]
        
        for lang in ["en", "hi", "mr"]:
            templates = craft["speech_inputs"][lang]
            
            for _ in range(num_variations_per_craft):
                # Pick random price rounded to 50
                price = random.randint(p_min // 50, p_max // 50) * 50
                template = random.choice(templates)
                raw_input = template.format(price=price)
                
                # Format 3 lines
                line1 = craft["history_heritage"]
                line2 = craft["originality_materials"]
                # Insert dynamic price into utility line
                utility_template = craft["utility_value"]
                if "priced at" not in utility_template.lower() and "{price}" not in utility_template:
                    line3 = f"{utility_template} Priced at an accessible ₹{price:,}, it offers remarkable lasting value."
                else:
                    line3 = utility_template.format(price=f"{price:,}")
                
                full_description = f"{line1}\n{line2}\n{line3}"

                # System instruction tailored for this task
                sys_instruct = (
                    "You are an expert e-commerce catalog copywriter for authentic Indian artisans and handicrafts. "
                    "Transform the artisan's informal spoken input into a rich, customer-ready 3-line product description in English: "
                    "Line 1 covers the craft identity, cultural heritage, and historical origin. "
                    "Line 2 covers material authenticity, purity, and traditional handcrafting artistry. "
                    "Line 3 covers utility, comfort, aesthetic appeal, and pricing value. "
                    "Output exactly 3 cohesive, polished sentences in English without extra commentary."
                )

                sample = {
                    "id": f"artisan_desc_{sample_id:04d}",
                    "craft_id": craft["craft_id"],
                    "craft_name": craft["name"],
                    "category": craft["category"],
                    "region": craft["region"],
                    "language": lang,
                    "raw_speech_input": raw_input,
                    "price_inr": price,
                    "line1_history_heritage": line1,
                    "line2_originality_material": line2,
                    "line3_utility_value": line3,
                    "full_3line_description": full_description,
                    # Qwen ChatML format
                    "messages": [
                        {"role": "system", "content": sys_instruct},
                        {"role": "user", "content": raw_input},
                        {"role": "assistant", "content": full_description}
                    ],
                    # Alpaca/Instruction format
                    "instruction": sys_instruct,
                    "input": raw_input,
                    "output": full_description
                }
                samples.append(sample)
                sample_id += 1

    return samples


def export_dataset(output_dir: str = "datasets"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)

    samples = generate_full_dataset(num_variations_per_craft=10)
    print(f"Generated {len(samples)} high-quality artisan description samples.")

    # 1. Export JSONL (for LLM training - fine-tuning with Hugging Face / trl)
    jsonl_path = os.path.join(output_dir, "artisan_rich_descriptions.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"[OK] Saved JSONL dataset to: {jsonl_path}")

    # 2. Export CSV (for human inspection, Excel, and data audits)
    csv_path = os.path.join(output_dir, "artisan_rich_descriptions.csv")
    fieldnames = [
        "id", "craft_id", "craft_name", "category", "region", "language",
        "raw_speech_input", "price_inr", "line1_history_heritage",
        "line2_originality_material", "line3_utility_value", "full_3line_description"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for s in samples:
            writer.writerow(s)
    print(f"[OK] Saved CSV dataset to: {csv_path}")

    # 3. Export Sample Preview Markdown
    md_path = os.path.join(output_dir, "DATASET_OVERVIEW.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Indian Artisan Rich 3-Line Product Description Dataset\n\n")
        f.write("### Overview\n")
        f.write("This dataset addresses the critical need of converting informal, terse artisan speech ")
        f.write("(e.g., *'kolhapuri chappal, pure leather, 1000 rs'*) into rich, customer-ready, ")
        f.write("3-line e-commerce descriptions highlighting craft heritage, authenticity, and utility.\n\n")
        f.write("### 3-Line Description Standard\n")
        f.write("- **Line 1 (Craft & History)**: Traditional craft identity, geographical origin, and 2-word/century royal/cultural history.\n")
        f.write("- **Line 2 (Originality & Materials)**: 100% pure authentic materials (vegetable tanned leather, pure zari, raw silk, virgin brass) and handcrafting techniques.\n")
        f.write("- **Line 3 (Comfort, Utility & Value)**: Wearability, festive/daily elegance, durability, and fair-trade pricing value.\n\n")
        f.write(f"### Total Samples: {len(samples)}\n")
        f.write("- **English inputs**: {}\n".format(sum(1 for s in samples if s['language'] == 'en')))
        f.write("- **Hindi inputs**: {}\n".format(sum(1 for s in samples if s['language'] == 'hi')))
        f.write("- **Marathi inputs**: {}\n\n".format(sum(1 for s in samples if s['language'] == 'mr')))
        f.write("### Featured Indian Crafts Covered\n")
        for craft in CRAFT_KNOWLEDGE:
            f.write(f"- **{craft['name']}** ({craft['region']}) — *{craft['category']}*\n")
        
        f.write("\n### Sample Pairings\n\n")
        for s in samples[:9]:
            f.write(f"#### [{s['language'].upper()}] {s['craft_name']}\n")
            f.write(f"**Artisan Raw Input:** `{s['raw_speech_input']}`\n\n")
            f.write(f"**Generated 3-Line Description:**\n\n> {s['full_3line_description'].replace(chr(10), chr(10) + '> ')}\n\n")
            f.write("---\n")
    print(f"[OK] Saved Overview documentation to: {md_path}")


if __name__ == "__main__":
    export_dataset()
