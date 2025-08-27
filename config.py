#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações e presets para diferentes tipos de lente fisheye
"""

# Presets para diferentes tipos de lente fisheye
FISHEYE_PRESETS = {
    "stereographic": {
        "name": "Stereographic (Padrão)",
        "description": "Lente estereográfica - boa para a maioria das lentes fisheye",
        "params": {
            "fov": 180,
            "pfov": 140,
            "dtype": "stereographic",
            "format": "fullframe",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    },
    
    "linear": {
        "name": "Linear (Equidistante)",
        "description": "Lente equidistante - mantém proporções lineares",
        "params": {
            "fov": 180,
            "pfov": 120,
            "dtype": "linear",
            "format": "fullframe",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    },
    
    "equalarea": {
        "name": "Equal Area (Equisólida)",
        "description": "Lente equisólida - preserva áreas",
        "params": {
            "fov": 180,
            "pfov": 130,
            "dtype": "equalarea",
            "format": "circular",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    },
    
    "orthographic": {
        "name": "Orthographic (Ortográfica)",
        "description": "Lente ortográfica - projeção ortográfica",
        "params": {
            "fov": 180,
            "pfov": 110,
            "dtype": "orthographic",
            "format": "fullframe",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    },
    
    "ultra_wide": {
        "name": "Ultra Wide",
        "description": "Para lentes ultra wide angle",
        "params": {
            "fov": 140,
            "pfov": 90,
            "dtype": "stereographic",
            "format": "fullframe",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    },
    
    "circular": {
        "name": "Circular",
        "description": "Para imagens fisheye circulares",
        "params": {
            "fov": 180,
            "pfov": 140,
            "dtype": "stereographic",
            "format": "circular",
            "xcenter": None,
            "ycenter": None,
            "radius": None,
            "angle": 0,
            "pad": 0
        }
    }
}

# Configurações de interface
UI_CONFIG = {
    "window_title": "Correção de Lente Fisheye - Aplicação Integrada",
    "window_size": "1200x800",
    "image_display_size": (400, 400),
    "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
    "default_output_format": ".jpg"
}

# Configurações de processamento
PROCESSING_CONFIG = {
    "interpolation_method": "cv2.INTER_LINEAR",
    "border_mode": "cv2.BORDER_CONSTANT",
    "default_pad_value": 0
}

# Configurações de validação
VALIDATION_CONFIG = {
    "fov_range": (0, 180),
    "pfov_range": (0, 180),
    "angle_range": (0, 360),
    "radius_range": (0, float('inf')),
    "pad_range": (0, 1000)
}

def get_preset(preset_name):
    """Retorna os parâmetros de um preset específico"""
    if preset_name in FISHEYE_PRESETS:
        return FISHEYE_PRESETS[preset_name]["params"].copy()
    else:
        raise ValueError(f"Preset '{preset_name}' não encontrado")

def list_presets():
    """Lista todos os presets disponíveis"""
    return list(FISHEYE_PRESETS.keys())

def get_preset_info(preset_name):
    """Retorna informações sobre um preset"""
    if preset_name in FISHEYE_PRESETS:
        return {
            "name": FISHEYE_PRESETS[preset_name]["name"],
            "description": FISHEYE_PRESETS[preset_name]["description"],
            "params": FISHEYE_PRESETS[preset_name]["params"]
        }
    else:
        raise ValueError(f"Preset '{preset_name}' não encontrado")

def validate_params(params):
    """Valida os parâmetros de entrada"""
    errors = []
    
    # Valida FOV
    if not VALIDATION_CONFIG["fov_range"][0] <= params.get("fov", 180) <= VALIDATION_CONFIG["fov_range"][1]:
        errors.append(f"FOV deve estar entre {VALIDATION_CONFIG['fov_range'][0]} e {VALIDATION_CONFIG['fov_range'][1]}")
    
    # Valida PFOV
    if not VALIDATION_CONFIG["pfov_range"][0] <= params.get("pfov", 140) <= VALIDATION_CONFIG["pfov_range"][1]:
        errors.append(f"PFOV deve estar entre {VALIDATION_CONFIG['pfov_range'][0]} e {VALIDATION_CONFIG['pfov_range'][1]}")
    
    # Valida angle
    angle = params.get("angle", 0)
    if angle is not None and angle != -1:
        if not VALIDATION_CONFIG["angle_range"][0] <= angle <= VALIDATION_CONFIG["angle_range"][1]:
            errors.append(f"Angle deve estar entre {VALIDATION_CONFIG['angle_range'][0]} e {VALIDATION_CONFIG['angle_range'][1]}")
    
    # Valida radius
    radius = params.get("radius", None)
    if radius is not None and radius != -1:
        if radius < VALIDATION_CONFIG["radius_range"][0]:
            errors.append(f"Radius deve ser maior que {VALIDATION_CONFIG['radius_range'][0]}")
    
    # Valida pad
    pad = params.get("pad", 0)
    if not VALIDATION_CONFIG["pad_range"][0] <= pad <= VALIDATION_CONFIG["pad_range"][1]:
        errors.append(f"Pad deve estar entre {VALIDATION_CONFIG['pad_range'][0]} e {VALIDATION_CONFIG['pad_range'][1]}")
    
    # Valida dtype
    valid_dtypes = ["linear", "equalarea", "orthographic", "stereographic"]
    if params.get("dtype", "stereographic") not in valid_dtypes:
        errors.append(f"Dtype deve ser um dos: {', '.join(valid_dtypes)}")
    
    # Valida format
    valid_formats = ["fullframe", "circular"]
    if params.get("format", "fullframe") not in valid_formats:
        errors.append(f"Format deve ser um dos: {', '.join(valid_formats)}")
    
    return errors

def get_default_params():
    """Retorna os parâmetros padrão"""
    return get_preset("stereographic")

