from database import get_database
from datetime import datetime
import hashlib

def init_db():
    db = get_database()
    if db is None:
        return

    # Clean start (optional - be careful in production!)
    print("Dropping existing collections for a clean initialization...")
    # Drop all existing collections to ensure a clean slate before re-initializing
    try:
        for name in db.list_collection_names():
            db.drop_collection(name)
    except Exception as e:
        print(f"Warning: could not drop all collections: {e}")

    # --- Collections and Indexes ---
    
    # Usuarios (Users)
    print("Initializing 'usuarios'...")
    db.usuarios.create_index("email", unique=True)
    
    # Create an admin user and a regular customer
    users_data = [
        {
            "nombre": "Admin User",
            "email": "admin@tienda.com",
            "password": hashlib.sha256("admin123".encode()).hexdigest(), # Simple hash for demo
            "role": "admin",
            "telefono": "1234567890",
            "direcciones": [],
            "fecha_registro": datetime.utcnow(),
            "estado": "activo",
            "preferencias": {"idioma": "es", "moneda": "USD"}
        },
        {
            "nombre": "Juan Perez",
            "email": "juan@example.com",
            "password": hashlib.sha256("user123".encode()).hexdigest(),
            "role": "customer",
            "telefono": "0987654321",
            "direcciones": [
                {
                    "alias": "Casa",
                    "calle": "Calle Falsa 123",
                    "ciudad": "Springfield",
                    "pais": "Simyland",
                    "codigo_postal": "12345"
                }
            ],
            "fecha_registro": datetime.utcnow(),
            "estado": "activo",
            "preferencias": {"idioma": "es", "moneda": "USD"}
        }
    ]
    db.usuarios.insert_many(users_data)


    # ============================
    #       CATEGORÍAS BASE
    # ============================

    # Tecnología
    tech_category = {
        "nombre": "Tecnología",
        "slug": "tecnologia",
        "descripcion": "Gadgets y electrónicos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    tech_id = db.categorias.insert_one(tech_category).inserted_id

    # Ropa
    clothing_category = {
        "nombre": "Ropa",
        "slug": "ropa",
        "descripcion": "Moda para todos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    clothing_id = db.categorias.insert_one(clothing_category).inserted_id

    # Coleccionables (antes Juguetes)
    collectibles_category = {
        "nombre": "Coleccionables",
        "slug": "coleccionables",
        "descripcion": "Figuras de acción, colecciones y artículos especiales",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    collectibles_id = db.categorias.insert_one(collectibles_category).inserted_id


    # ============================
    #     SUBCATEGORÍAS TECNOLOGÍA
    # ============================

    # Laptops (ya existente)
    laptops_category = {
        "nombre": "Laptops",
        "slug": "laptops",
        "descripcion": "Portátiles de alto rendimiento",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    laptops_id = db.categorias.insert_one(laptops_category).inserted_id

    # Smartphones
    smartphones_category = {
        "nombre": "Smartphones",
        "slug": "smartphones",
        "descripcion": "Teléfonos inteligentes",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    smartphones_id = db.categorias.insert_one(smartphones_category).inserted_id

    # Auriculares
    headphones_category = {
        "nombre": "Auriculares",
        "slug": "auriculares",
        "descripcion": "Audífonos inalámbricos y alámbricos",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    headphones_id = db.categorias.insert_one(headphones_category).inserted_id

    # Monitores
    monitors_category = {
        "nombre": "Monitores",
        "slug": "monitores",
        "descripcion": "Pantallas para computadora",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    monitors_id = db.categorias.insert_one(monitors_category).inserted_id


    # ============================
    #     SUBCATEGORÍAS COLECCIONABLES
    # ============================

    # Figuras de Acción
    action_figures_category = {
        "nombre": "Figuras de Acción",
        "slug": "figuras-de-accion",
        "descripcion": "Figuras de colección articuladas o estáticas",
        "parent_id": collectibles_id,
        "fecha_creacion": datetime.utcnow()
    }
    action_figures_id = db.categorias.insert_one(action_figures_category).inserted_id

    # Cartas Coleccionables
    cards_category = {
        "nombre": "Cartas Coleccionables",
        "slug": "cartas",
        "descripcion": "TCG: Pokémon, Yu-Gi-Oh, MTG y más",
        "parent_id": collectibles_id,
        "fecha_creacion": datetime.utcnow()
    }
    cards_id = db.categorias.insert_one(cards_category).inserted_id


    # ============================
    #   SUBCATEGORÍAS DE ROPA
    # ============================

    hoodies_category = {
        "nombre": "Buzos",
        "slug": "buzos",
        "descripcion": "Sudaderas y hoodies",
        "parent_id": clothing_id,
        "fecha_creacion": datetime.utcnow()
    }
    hoodies_id = db.categorias.insert_one(hoodies_category).inserted_id

    tshirts_category = {
        "nombre": "Camisetas",
        "slug": "camisetas",
        "descripcion": "Camisetas casuales",
        "parent_id": clothing_id,
        "fecha_creacion": datetime.utcnow()
    }
    tshirts_id = db.categorias.insert_one(tshirts_category).inserted_id

    skirts_category = {
        "nombre": "Faldas",
        "slug": "faldas",
        "descripcion": "Faldas casuales y de vestir",
        "parent_id": clothing_id,
        "fecha_creacion": datetime.utcnow()
    }
    skirts_id = db.categorias.insert_one(skirts_category).inserted_id

    soccer_category = {
        "nombre": "Camisetas Deportivas",
        "slug": "camisetas-deportivas",
        "descripcion": "Camisetas deportivas oficiales",
        "parent_id": clothing_id,
        "fecha_creacion": datetime.utcnow()
    }
    soccer_id = db.categorias.insert_one(soccer_category).inserted_id

    # ============================
    #   SUBCATEGORÍAS GAFAS / JOYERÍA
    # ============================

    smart_glasses_category = {
        "nombre": "Gafas Inteligentes",
        "slug": "gafas-inteligentes",
        "descripcion": "Gafas con funciones inteligentes",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    smart_glasses_id = db.categorias.insert_one(smart_glasses_category).inserted_id

    jewelry_category = {
        "nombre": "Joyería",
        "slug": "joyeria",
        "descripcion": "Anillos, cadenas y accesorios",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    jewelry_id = db.categorias.insert_one(jewelry_category).inserted_id

    mens_jewelry_category = {
        "nombre": "Joyería para Hombre",
        "slug": "joyeria-hombre",
        "descripcion": "Accesorios masculinos",
        "parent_id": jewelry_id,
        "fecha_creacion": datetime.utcnow()
    }
    mens_jewelry_id = db.categorias.insert_one(mens_jewelry_category).inserted_id


    # ============================
    #        ÍNDICES PRODUCTOS
    # ============================

    db.productos.create_index("sku", unique=True)
    db.productos.create_index("nombre", unique=False)


    # ============================
    #         PRODUCTOS
    # ============================

    products_data = [

        # ============================================
        #               L A P T O P S
        # ============================================

        {
            "sku": "LAP-001",
            "nombre": "Laptop Pro X",
            "descripcion": "La mejor laptop para desarrolladores",
            "categoria": {"id": laptops_id, "nombre": "Laptops"},
            "precio": 150000,
            "moneda": "USD",
            "stock": 50,
            "atributos": {"marca": "TechBrand", "color": "Gris Espacial", "ram": "16GB"},
            "imagenes": [
                "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/B03-Surface-Laptop-13-inch-1Ed-Rational-Violet-Rear-Right"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "LAP-002",
            "nombre": "Laptop Ultra Slim",
            "descripcion": "Liviana y potente, ideal para estudiantes",
            "categoria": {"id": laptops_id, "nombre": "Laptops"},
            "precio": 89999,
            "moneda": "USD",
            "stock": 70,
            "atributos": {"marca": "LiteTech", "color": "Plateado", "ram": "8GB"},
            "imagenes": [
                "https://www.gatewayusa.com/cdn/shop/files/black16_f7c7d052-2222-427e-9dc6-174f2928718f.png?v=1721623728&width=1400"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #            S M A R T P H O N E S
        # ============================================

        {
            "sku": "SMA-001",
            "nombre": "Smartphone Max 12",
            "descripcion": "Pantalla OLED 6.7\", 5G y triple cámara",
            "categoria": {"id": smartphones_id, "nombre": "Smartphones"},
            "precio": 99900,
            "moneda": "USD",
            "stock": 120,
            "atributos": {"marca": "PhoneTech", "color": "Negro", "almacenamiento": "128GB"},
            "imagenes": [
                "https://images.fonearena.com/blog/wp-content/uploads/2022/07/Samsung-Galaxy-S22-Bora-Purple-1024x911.jpg"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "SMA-002",
            "nombre": "Smartphone Lite A5",
            "descripcion": "Económico, rápido y con buena cámara",
            "categoria": {"id": smartphones_id, "nombre": "Smartphones"},
            "precio": 29900,
            "moneda": "USD",
            "stock": 200,
            "atributos": {"marca": "NovaPhone", "color": "Azul", "almacenamiento": "64GB"},
            "imagenes": [
                "https://http2.mlstatic.com/D_NQ_NP_772634-MCO70066305388_062023-O.webp"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #            A U R I C U L A R E S
        # ============================================

        {
            "sku": "AUR-001",
            "nombre": "Auriculares ProSound",
            "descripcion": "Sonido Hi-Fi y cancelación activa de ruido",
            "categoria": {"id": headphones_id, "nombre": "Auriculares"},
            "precio": 19999,
            "moneda": "USD",
            "stock": 150,
            "atributos": {"marca": "SoundMax", "tipo": "Inalámbricos"},
            "imagenes": [
                "https://rukminim2.flixcart.com/image/480/640/xif0q/headphone/a/k/i/-original-imahyfkkhwpeb7ze.jpeg?q=90"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "AUR-002",
            "nombre": "Auriculares BassBoost",
            "descripcion": "Sonido profundo y batería de 30 horas",
            "categoria": {"id": headphones_id, "nombre": "Auriculares"},
            "precio": 14999,
            "moneda": "USD",
            "stock": 180,
            "atributos": {"marca": "BeatFlex", "tipo": "Over-Ear"},
            "imagenes": [
                "https://www.sony.com.co/image/5d02da5df552836db894cead8a68f5f3?fmt=pjpeg&wid=330&bgcolor=FFFFFF&bgc=FFFFFF"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #              M O N I T O R E S
        # ============================================

        {
            "sku": "MON-001",
            "nombre": "Monitor UltraWide 34\"",
            "descripcion": "Pantalla curva para multitarea",
            "categoria": {"id": monitors_id, "nombre": "Monitores"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 40,
            "atributos": {"marca": "ViewMax", "resolución": "3440x1440"},
            "imagenes": [
                "https://www.lg.com/content/dam/channel/wcms/co/images/monitores/34wq500-b/gallery/ultrawide-34wq500-gallery-01-2010.jpg/_jcr_content/renditions/thum-1600x1062.jpeg"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "MON-002",
            "nombre": "Monitor Gamer 27\"",
            "descripcion": "165Hz, 1ms, ideal para gaming competitivo",
            "categoria": {"id": monitors_id, "nombre": "Monitores"},
            "precio": 29999,
            "moneda": "USD",
            "stock": 60,
            "atributos": {"marca": "GamerTech", "resolución": "1440p"},
            "imagenes": [
                "https://es-store.msi.com/cdn/shop/files/monitor-gaming-msi-mag-27c6x.png?v=1733326643&width=640"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #      C O L E C C I O N A B L E S
        # ============================================

        # Figuras de Acción
        {
            "sku": "FIG-001",
            "nombre": "Figura de Acción Daredevil",
            "descripcion": "Figura articulada de edición limitada",
            "categoria": {"id": action_figures_id, "nombre": "Figuras de Acción"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 80,
            "atributos": {"franquicia": "Marvel", "altura": "25 cm"},
            "imagenes": ["https://alteregocomics.com/cdn/shop/files/hot-toys-marvel-daredevil-sixth-scale-figure-gallery-67eabdb51471c.jpg?v=1743442148&width=1946"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "FIG-002",
            "nombre": "Punisher",
            "descripcion": "Figura articulada de edición limitada",
            "categoria": {"id": action_figures_id, "nombre": "Figuras de Acción"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 50,
            "atributos": {"franquicia": "Marvel", "altura": "25 cm"},
            "imagenes": ["https://m.media-amazon.com/images/I/81W0CWI3DNL.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # Cartas coleccionables
        {
            "sku": "CAR-001",
            "nombre": "Sobre Pokémon TCG",
            "descripcion": "Sobre con 10 cartas al azar",
            "categoria": {"id": cards_id, "nombre": "Cartas Coleccionables"},
            "precio": 499,
            "moneda": "USD",
            "stock": 300,
            "atributos": {"marca": "Pokémon", "tipo": "Expansión actual"},
            "imagenes": ["https://xtremeplay.co/wp-content/uploads/2023/03/TOYCOLPOK1312_1.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CAR-002",
            "nombre": "Exploding Kittens Party Pack",
            "descripcion": "Mazo para 10 jugadores",
            "categoria": {"id": cards_id, "nombre": "Cartas Coleccionables"},
            "precio": 1499,
            "moneda": "USD",
            "stock": 120,
            "atributos": {"marca": "Exploding Kittens", "tipo": "Party Pack"},
            "imagenes": ["https://media.falabella.com/falabellaCO/124472703_01/w=1500,h=1500,fit=pad"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        }
        
    ]

    db.productos.insert_many(products_data)

    # ============================
    #       PRODUCTOS NUEVOS
    # ============================

    # Nota: precios en centavos para mantener consistencia con el resto del init_db.py
    additional_products = [
        {
            "sku": "TECH-GLASS-001",
            "nombre": "Gafas Inteligentes VisionX",
            "descripcion": "Gafas inteligentes con asistente integrado, cámara HD y conectividad Bluetooth.",
            "categoria": {"id": smart_glasses_id, "nombre": "Gafas Inteligentes"},
            "precio": 14999,           # $149.99 -> 14999 centavos
            "moneda": "USD",
            "stock": 25,
            "atributos": {"marca": "VisionX", "color": "Negro", "conectividad": "Bluetooth"},
            "imagenes": ["https://http2.mlstatic.com/D_NQ_NP_622593-CBT78119687397_082024-O.webp"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CLOT-HOOD-001",
            "nombre": "Buzo Astronauta Galaxy",
            "descripcion": "Buzo con estampado de astronauta, material suave y cálido.",
            "categoria": {"id": hoodies_id, "nombre": "Buzos"},
            "precio": 3999,            # $39.99
            "moneda": "USD",
            "stock": 40,
            "atributos": {"marca": "GalaxyWear", "talla": "M"},
            "imagenes": ["https://acdn-us.mitiendanube.com/stores/002/114/613/products/a93ce007-639a-4ac1-8f63-934274b666801-a5a526f854751ddf4b16494526294213-640-0.png"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CLOT-SHIRT-001",
            "nombre": "Camiseta Blanca Básica",
            "descripcion": "Camiseta blanca ligera y cómoda, ideal para uso diario.",
            "categoria": {"id": tshirts_id, "nombre": "Camisetas"},
            "precio": 1499,            # $14.99
            "moneda": "USD",
            "stock": 100,
            "atributos": {"marca": "BasicWear", "talla": "L"},
            "imagenes": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRdWIhVeC5aGhe4z7cRU_D4y98fVzql46mhdA&s"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "JEW-MAN-NECK-001",
            "nombre": "Collar para Hombre Titan",
            "descripcion": "Collar elegante con acabado dorado y piedra brillante.",
            "categoria": {"id": mens_jewelry_id, "nombre": "Joyería para Hombre"},
            "precio": 2999,            # $29.99
            "moneda": "USD",
            "stock": 50,
            "atributos": {"material": "Aleación", "acabado": "Dorado"},
            "imagenes": ["https://cdn-media.glamira.com/media/product/newgeneration/view/1/sku/14976lobris-2.50/diamond/diamond-zirconia_AAAAA/alloycolour/yellow.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "JEW-RING-001",
            "nombre": "Anillo de Oro Royal",
            "descripcion": "Anillo de oro con incrustaciones brillantes.",
            "categoria": {"id": jewelry_id, "nombre": "Joyería"},
            "precio": 49999,           # $499.99
            "moneda": "USD",
            "stock": 10,
            "atributos": {"material": "Oro", "talla": "10"},
            "imagenes": ["https://cdn-media.glamira.com/media/product/newgeneration/view/1/sku/15549gisu1/diamond/diamond-Brillant_AAA/stone2/diamond-Brillant_AAA/stone3/diamond-Brillant_AAA/alloycolour/yellow.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "JEW-RING-002",
            "nombre": "Anillo de Oro Blanco Aurora",
            "descripcion": "Anillo elegante de oro blanco, perfecto para ocasiones especiales.",
            "categoria": {"id": jewelry_id, "nombre": "Joyería"},
            "precio": 45999,           # $459.99
            "moneda": "USD",
            "stock": 12,
            "atributos": {"material": "Oro Blanco"},
            "imagenes": ["https://cdn-media.glamira.com/media/product/newgeneration/view/1/sku/22136bridal-rise05/diamond/lab-grown-diamond_AAA/alloycolour/white.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "JEW-RING-003",
            "nombre": "Anillo de Plata Clásico",
            "descripcion": "Anillo de plata pulida con diseño minimalista.",
            "categoria": {"id": jewelry_id, "nombre": "Joyería"},
            "precio": 7999,            # $79.99
            "moneda": "USD",
            "stock": 30,
            "atributos": {"material": "Plata"},
            "imagenes": ["https://cdn-media.glamira.com/media/product/newgeneration/view/1/sku/GWD210000/alloycolour/white/width/w4/profile/prA/surface/polished.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CLOT-SKIRT-001",
            "nombre": "Falda Beige Elegante",
            "descripcion": "Falda beige de corte clásico, ideal para outfits formales.",
            "categoria": {"id": skirts_id, "nombre": "Faldas"},
            "precio": 2499,            # $24.99
            "moneda": "USD",
            "stock": 35,
            "atributos": {"material": "Tela", "talla": "M"},
            "imagenes": ["https://aguamarinaoficial.com/cdn/shop/files/2_ce0477c4-cec0-4d51-be6e-0e6afd71e3d8.jpg?v=1750965921"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CLOT-SKIRT-002",
            "nombre": "Falda de Cuero Premium",
            "descripcion": "Falda de cuero sintético con acabado brillante.",
            "categoria": {"id": skirts_id, "nombre": "Faldas"},
            "precio": 4999,            # $49.99
            "moneda": "USD",
            "stock": 20,
            "atributos": {"material": "Cuero sintético"},
            "imagenes": ["https://m.media-amazon.com/images/I/41TsOKYhUlL._AC_UY1000_.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CLOT-SOCC-001",
            "nombre": "Camiseta Inter de Milán Oficial",
            "descripcion": "Camiseta original del Inter de Milán temporada actual.",
            "categoria": {"id": soccer_id, "nombre": "Camisetas Deportivas"},
            "precio": 8999,            # $89.99
            "moneda": "USD",
            "stock": 15,
            "atributos": {"equipo": "Inter de Milán", "talla": "L"},
            "imagenes": ["https://nikeco.vtexassets.com/arquivos/ids/873730/HJ4591_439_A_PREM.jpg?v=638839496465270000"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        }
    ]

    db.productos.insert_many(additional_products)


    # ============================
    #          PEDIDOS
    # ============================
    print("Initializing 'pedidos'...")
    # NOTE: Per configuration, do not insert default/example orders.
    # The 'pedidos' collection will be created empty.

    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
