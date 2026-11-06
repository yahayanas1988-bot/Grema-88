/*
  Contenu du site Grema88.
  Le plus simple : ouvrez admin.html (« Espace Grema »), faites vos changements,
  puis téléchargez le nouveau contenu.js et remplacez ce fichier.
  Vous pouvez aussi modifier ce fichier à la main : gardez les guillemets et les virgules.
*/
window.GREMA88 = {
  "agence": {
    "nom": "Grema88",
    "nomComplet": "Grema Agence 88",
    "slogan": "Des applications, des livres, des produits et des histoires du Sahel, pour l'Afrique et pour le monde.",
    "whatsapp": "",
    "email": "contact.grema88@gmail.com",
    "facebook": "",
    "tiktok": "",
    "instagram": "",
    "youtube": "",
    "villeMeteo": "Niamey"
  },
  "oeuvres": [
    {
      "id": "nessa-tazo-kussa",
      "type": "application",
      "titre": "Nessa Tazo Kussa",
      "accroche": "Taxi et moto, à portée de main",
      "description": "Commandez un taxi ou une moto en quelques secondes. L'application relie les clients, les chauffeurs, les agents et le patron dans un seul outil. Disponible en français, anglais, haoussa et arabe, pensée pour le Niger, le Nigeria et le Ghana.",
      "image": "images/logo-nessa-tazo-kussa.svg",
      "lien": "apps/nessa-tazo-kussa/",
      "bouton": "Essayer la démo",
      "prix": "",
      "auteur": "",
      "vendeur": "",
      "whatsapp": "",
      "ville": "",
      "tags": [
        "Taxi",
        "Moto",
        "4 langues"
      ],
      "statut": "disponible",
      "vedette": true,
      "traductions": {
        "en": {
          "accroche": "Taxi and moto rides, right at hand",
          "description": "Book a taxi or a motorbike in seconds. The app connects customers, drivers, agents and the owner in one tool. Available in French, English, Hausa and Arabic, built for Niger, Nigeria and Ghana.",
          "bouton": "Try the demo"
        },
        "ar": {
          "accroche": "تاكسي ودرّاجة نارية في متناول يدك",
          "description": "اطلب تاكسي أو درّاجة نارية في ثوانٍ. يربط التطبيق الزبائن والسائقين والوكلاء والمدير في أداة واحدة. متوفّر بالفرنسية والإنجليزية والهوسا والعربية، مصمّم للنيجر ونيجيريا وغانا.",
          "bouton": "جرّب النسخة التجريبية"
        },
        "de": {
          "accroche": "Taxi und Moto, immer griffbereit",
          "description": "Bestellen Sie in Sekunden ein Taxi oder ein Motorrad. Die App verbindet Kunden, Fahrer, Agenten und den Chef in einem Werkzeug. Auf Französisch, Englisch, Hausa und Arabisch, gemacht für Niger, Nigeria und Ghana.",
          "bouton": "Demo testen"
        }
      }
    },
    {
      "id": "rdv-pro",
      "type": "application",
      "titre": "RDV Pro",
      "accroche": "Les rendez-vous de votre activité, bien rangés",
      "description": "Une application web pour prendre et gérer les rendez-vous de vos clients. Vos clients réservent en ligne, vous voyez votre planning d'un coup d'œil.",
      "image": "images/logo-rdv-pro.svg",
      "lien": "https://rdv-pro.netlify.app",
      "bouton": "Ouvrir RDV Pro",
      "prix": "",
      "auteur": "",
      "vendeur": "",
      "whatsapp": "",
      "ville": "",
      "tags": [
        "Rendez-vous",
        "Professionnels"
      ],
      "statut": "disponible",
      "vedette": false,
      "traductions": {
        "en": {
          "accroche": "Your business appointments, neatly organised",
          "description": "A web app to take and manage your customers' appointments. Customers book online, you see your schedule at a glance.",
          "bouton": "Open RDV Pro"
        },
        "ar": {
          "accroche": "مواعيد عملك منظّمة",
          "description": "تطبيق ويب لأخذ مواعيد زبائنك وإدارتها. يحجز الزبائن عبر الإنترنت، وترى جدولك بنظرة واحدة.",
          "bouton": "افتح RDV Pro"
        },
        "de": {
          "accroche": "Die Termine Ihres Geschäfts, gut sortiert",
          "description": "Eine Web-App, um Kundentermine anzunehmen und zu verwalten. Ihre Kunden buchen online, Sie sehen Ihren Kalender auf einen Blick.",
          "bouton": "RDV Pro öffnen"
        }
      }
    },
    {
      "id": "exemple-tissu-wax",
      "type": "produit",
      "titre": "Pagne wax 6 yards",
      "accroche": "Exemple de produit vendeur",
      "description": "Exemple de fiche produit d'un vendeur. Le bouton ouvre WhatsApp avec le vendeur. Remplacez ou supprimez cet exemple dans l'Espace Grema.",
      "image": "",
      "lien": "",
      "bouton": "",
      "prix": "12 000 FCFA",
      "auteur": "",
      "vendeur": "Boutique exemple",
      "whatsapp": "",
      "ville": "Niamey",
      "tags": [
        "Tissu",
        "Exemple"
      ],
      "statut": "disponible",
      "vedette": false,
      "traductions": {
        "en": {
          "titre": "Wax fabric, 6 yards",
          "accroche": "Example seller product",
          "description": "Example of a seller's product page. The button opens WhatsApp with the seller."
        },
        "ar": {
          "titre": "قماش واكس 6 ياردات",
          "accroche": "مثال لمنتج بائع",
          "description": "مثال لصفحة منتج بائع. يفتح الزر واتساب مع البائع."
        },
        "de": {
          "titre": "Wax-Stoff, 6 Yards",
          "accroche": "Beispiel für ein Verkäuferprodukt",
          "description": "Beispiel einer Produktseite eines Verkäufers. Der Button öffnet WhatsApp mit dem Verkäufer."
        }
      }
    },
    {
      "id": "exemple-miel",
      "type": "produit",
      "titre": "Miel du Sahel, 1 litre",
      "accroche": "Exemple de produit vendeur",
      "description": "Deuxième exemple, pour voir le rendu de la boutique. Supprimez-le quand vos vrais vendeurs arrivent.",
      "image": "",
      "lien": "",
      "bouton": "",
      "prix": "5 000 FCFA",
      "auteur": "",
      "vendeur": "Ferme exemple",
      "whatsapp": "",
      "ville": "Zinder",
      "tags": [
        "Alimentation",
        "Exemple"
      ],
      "statut": "disponible",
      "vedette": false,
      "traductions": {
        "en": {
          "titre": "Sahel honey, 1 litre",
          "accroche": "Example seller product",
          "description": "Second example to show how the shop looks."
        },
        "ar": {
          "titre": "عسل الساحل، لتر واحد",
          "accroche": "مثال لمنتج بائع",
          "description": "مثال ثانٍ لعرض شكل المتجر."
        },
        "de": {
          "titre": "Sahel-Honig, 1 Liter",
          "accroche": "Beispiel für ein Verkäuferprodukt",
          "description": "Zweites Beispiel, um den Shop zu zeigen."
        }
      }
    },
    {
      "id": "le-conseil-de-la-savane",
      "type": "autre",
      "titre": "Le Conseil de la Savane",
      "accroche": "Une fable sur le pouvoir et la stratégie",
      "description": "Dessin animé de 5 minutes. La pluie n'est pas venue, le lac rétrécit, et le roi lion Kadar réunit son conseil sur le Rocher du Soleil. La hyène veut la guerre, le renard veut mentir, la chouette propose une autre voie.",
      "image": "images/conseil-savane.jpg",
      "lien": "videos/le-conseil-de-la-savane.mp4",
      "bouton": "Regarder",
      "prix": "",
      "auteur": "Grema88",
      "vendeur": "",
      "whatsapp": "",
      "ville": "",
      "tags": [
        "Dessin animé",
        "5 min",
        "Fable"
      ],
      "statut": "disponible",
      "vedette": false,
      "traductions": {
        "en": {
          "titre": "The Savannah Council",
          "accroche": "A fable about power and strategy",
          "description": "A 5-minute cartoon, in French. The rain has not come, the lake is shrinking, and Kadar the lion king gathers his council on Sun Rock. The hyena wants war, the fox wants to lie, the owl offers another way.",
          "bouton": "Watch"
        },
        "ar": {
          "titre": "مجلس السافانا",
          "accroche": "حكاية عن السلطة والاستراتيجية",
          "description": "رسوم متحركة مدّتها 5 دقائق، بالفرنسية. لم يأتِ المطر، والبحيرة تجفّ، فيجمع الملك الأسد قادر مجلسه على صخرة الشمس. الضبع يريد الحرب، والثعلب يريد الكذب، والبومة تقترح طريقاً آخر.",
          "bouton": "مشاهدة"
        },
        "de": {
          "titre": "Der Rat der Savanne",
          "accroche": "Eine Fabel über Macht und Strategie",
          "description": "Ein 5-minütiger Zeichentrickfilm auf Französisch. Der Regen bleibt aus, der See schrumpft, und Löwenkönig Kadar ruft seinen Rat auf dem Sonnenfelsen zusammen. Die Hyäne will Krieg, der Fuchs will lügen, die Eule zeigt einen anderen Weg.",
          "bouton": "Ansehen"
        }
      }
    },
    {
      "id": "exemple-livre-1",
      "type": "livre",
      "titre": "Le titre de votre livre",
      "accroche": "Exemple de fiche livre",
      "description": "Ceci est un exemple. Remplacez-le par votre vrai livre dans l'Espace Grema : titre, auteur, résumé, couverture, prix et lien d'achat ou de lecture.",
      "image": "",
      "lien": "",
      "bouton": "Lire un extrait",
      "prix": "2 500 FCFA",
      "auteur": "Grema",
      "vendeur": "",
      "whatsapp": "",
      "ville": "",
      "tags": [
        "Roman",
        "Exemple"
      ],
      "statut": "bientot",
      "vedette": false,
      "traductions": {
        "en": {
          "titre": "Your book title",
          "accroche": "Example book page",
          "description": "This is an example book page."
        },
        "ar": {
          "titre": "عنوان كتابك",
          "accroche": "مثال لصفحة كتاب",
          "description": "هذه صفحة كتاب للمثال."
        },
        "de": {
          "titre": "Der Titel Ihres Buches",
          "accroche": "Beispiel einer Buchseite",
          "description": "Dies ist eine Beispiel-Buchseite."
        }
      }
    }
  ],
  "actualites": [
    {
      "id": "actu-boutique",
      "date": "2026-10-30",
      "titre": "Nouveau : vendez vos produits sur Grema 88",
      "texte": "Artisans, commerçants et créateurs peuvent maintenant proposer leurs produits sur le site. Les clients commandent directement sur WhatsApp, en français, anglais, arabe ou allemand.",
      "image": "",
      "lien": "#vendre",
      "traductions": {
        "en": {
          "titre": "New: sell your products on Grema 88",
          "texte": "Artisans, shop owners and creators can now list their products on the site. Customers order directly on WhatsApp, in French, English, Arabic or German."
        },
        "ar": {
          "titre": "جديد: بِع منتجاتك على غريما 88",
          "texte": "يمكن للحرفيين والتجار والمبدعين الآن عرض منتجاتهم على الموقع. يطلب الزبائن مباشرة عبر واتساب، بالفرنسية أو الإنجليزية أو العربية أو الألمانية."
        },
        "de": {
          "titre": "Neu: Verkaufen Sie Ihre Produkte auf Grema 88",
          "texte": "Handwerker, Händler und Kreative können ihre Produkte jetzt auf der Website anbieten. Kunden bestellen direkt per WhatsApp, auf Französisch, Englisch, Arabisch oder Deutsch."
        }
      }
    },
    {
      "id": "actu-site",
      "date": "2026-10-30",
      "titre": "Le site de l'agence Grema 88 ouvre ses portes",
      "texte": "Retrouvez ici toutes nos créations : l'application de taxi et moto Nessa Tazo Kussa, RDV Pro, nos livres et notre dessin animé « Le Conseil de la Savane ».",
      "image": "images/partage.jpg",
      "lien": "#catalogue",
      "traductions": {
        "en": {
          "titre": "The Grema 88 agency website is open",
          "texte": "Find all our creations here: the Nessa Tazo Kussa taxi and moto app, RDV Pro, our books and our cartoon \"The Savannah Council\"."
        },
        "ar": {
          "titre": "افتتاح موقع وكالة غريما 88",
          "texte": "اكتشفوا هنا كل إبداعاتنا: تطبيق التاكسي والدرّاجات نيسا تازو كوسا، وRDV Pro، وكتبنا، ورسومنا المتحركة «مجلس السافانا»."
        },
        "de": {
          "titre": "Die Website der Agentur Grema 88 ist online",
          "texte": "Hier finden Sie alle unsere Werke: die Taxi- und Moto-App Nessa Tazo Kussa, RDV Pro, unsere Bücher und unseren Zeichentrickfilm „Der Rat der Savanne“."
        }
      }
    }
  ],
  "evenements": []
};
