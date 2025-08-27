#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Integrada de Correção de Lente Fisheye
Combina o algoritmo do defisheye com interface interativa

Desenvolvido baseado nos projetos:
- defisheye: https://github.com/duducosmos/defisheye
- Fish-Eye-Lens-Correction: https://github.com/your-repo/Fish-Eye-Lens-Correction
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from numpy import arange, sqrt, arctan, sin, tan, meshgrid, pi, pad
from numpy import ndarray, hypot
from config import validate_params


class DefisheyeAlgorithm:
    """
    Algoritmo de correção fisheye baseado no projeto defisheye original
    """
    def __init__(self, infile, **kwargs):
        vkwargs = {"fov": 180,
                   "pfov": 120,
                   "xcenter": None,
                   "ycenter": None,
                   "radius": None,
                   "pad": 0,
                   "angle": 0,
                   "dtype": "equalarea",
                   "format": "fullframe"
                   }
        self._start_att(vkwargs, kwargs)

        if type(infile) == str:
            _image = cv2.imread(infile)
        elif type(infile) == ndarray:
            _image = infile
        else:
            raise Exception("Image format not recognized")

        if self._pad > 0:
            _image = cv2.copyMakeBorder(
                _image, self._pad, self._pad, self._pad, self._pad, cv2.BORDER_CONSTANT)

        width = _image.shape[1]
        height = _image.shape[0]
        xcenter = width // 2
        ycenter = height // 2

        dim = min(width, height)
        x0 = xcenter - dim // 2
        xf = xcenter + dim // 2
        y0 = ycenter - dim // 2
        yf = ycenter + dim // 2

        self._image = _image[y0:yf, x0:xf, :]

        self._width = self._image.shape[1]
        self._height = self._image.shape[0]

        if self._xcenter is None:
            self._xcenter = (self._width - 1) // 2

        if self._ycenter is None:
            self._ycenter = (self._height - 1) // 2

    def _map(self, i, j, ofocinv, dim):
        xd = i - self._xcenter
        yd = j - self._ycenter

        rd = hypot(xd, yd)
        phiang = arctan(ofocinv * rd)

        if self._dtype == "linear":
            ifoc = dim * 180 / (self._fov * pi)
            rr = ifoc * phiang

        elif self._dtype == "equalarea":
            ifoc = dim / (2.0 * sin(self._fov * pi / 720))
            rr = ifoc * sin(phiang / 2)

        elif self._dtype == "orthographic":
            ifoc = dim / (2.0 * sin(self._fov * pi / 360))
            rr = ifoc * sin(phiang)

        elif self._dtype == "stereographic":
            ifoc = dim / (2.0 * tan(self._fov * pi / 720))
            rr = ifoc * tan(phiang / 2)

        rdmask = rd != 0
        xs = xd.astype(np.float32).copy()
        ys = yd.astype(np.float32).copy()

        xs[rdmask] = (rr[rdmask] / rd[rdmask]) * xd[rdmask] + self._xcenter
        ys[rdmask] = (rr[rdmask] / rd[rdmask]) * yd[rdmask] + self._ycenter

        xs[~rdmask] = 0
        ys[~rdmask] = 0

        return xs, ys

    def convert(self, outfile=None):
        if self._format == "circular":
            dim = min(self._width, self._height)
        elif self._format == "fullframe":
            dim = sqrt(self._width ** 2.0 + self._height ** 2.0)

        if self._radius is not None:
            dim = 2 * self._radius

        # compute output (perspective) focal length and its inverse from ofov
        # phi=fov/2; r=N/2
        # r/f=tan(phi);
        # f=r/tan(phi);
        # f= (N/2)/tan((fov/2)*(pi/180)) = N/(2*tan(fov*pi/360))

        ofoc = dim / (2 * tan(self._pfov * pi / 360))
        ofocinv = 1.0 / ofoc

        i = arange(self._width)
        j = arange(self._height)
        i, j = meshgrid(i, j)

        xs, ys, = self._map(i, j, ofocinv, dim)

        img = cv2.remap(self._image, xs, ys, cv2.INTER_LINEAR)
        if outfile is not None:
            cv2.imwrite(outfile, img)
        return img

    def _start_att(self, vkwargs, kwargs):
        """Starting attributes"""
        pin = []

        for key, value in kwargs.items():
            if key not in vkwargs:
                raise NameError("Invalid key {}".format(key))
            else:
                pin.append(key)
                setattr(self, "_{}".format(key), value)

        pin = set(pin)
        rkeys = set(vkwargs.keys()) - pin
        for key in rkeys:
            setattr(self, "_{}".format(key), vkwargs[key])


class IntegratedDefisheyeApp:
    """
    Aplicação integrada com interface gráfica para correção de lente fisheye
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Correção de Lente Fisheye - Aplicação Integrada")
        self.root.geometry("1200x800")
        
        # Variáveis para armazenar a imagem
        self.original_image = None
        self.original_image_path = None
        self.processed_image = None
        
        # Variáveis para os parâmetros (editáveis) - usando valores padrão do defisheye original
        self.fov_var = tk.IntVar(value=180)
        self.pfov_var = tk.IntVar(value=120)
        self.xcenter_var = tk.IntVar(value=-1)
        self.ycenter_var = tk.IntVar(value=-1)
        self.radius_var = tk.DoubleVar(value=-1)
        self.angle_var = tk.IntVar(value=0)
        self.dtype_var = tk.StringVar(value="equalarea")
        self.format_var = tk.StringVar(value="fullframe")
        self.pad_var = tk.IntVar(value=0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Barra de ferramentas superior
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de arquivo
        ttk.Button(toolbar_frame, text="📁 Abrir Imagem", command=self.open_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar_frame, text="💾 Salvar Resultado", command=self.save_result).pack(side=tk.LEFT, padx=(0, 10))
        
        # Presets
        ttk.Label(toolbar_frame, text="Presets:").pack(side=tk.LEFT, padx=(20, 5))
        self.preset_var = tk.StringVar(value="equalarea")
        preset_combo = ttk.Combobox(toolbar_frame, textvariable=self.preset_var, 
                                   values=["stereographic", "linear", "equalarea", "orthographic"], state="readonly", width=15)
        preset_combo.pack(side=tk.LEFT, padx=(0, 10))
        preset_combo.bind('<<ComboboxSelected>>', self.apply_preset)
        
        ttk.Button(toolbar_frame, text="ℹ️ Info", command=self.show_preset_info).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de parâmetros (lado esquerdo)
        params_frame = ttk.LabelFrame(main_frame, text="Parâmetros de Correção", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Parâmetros editáveis
        self.create_parameter_widgets(params_frame)
        
        # Frame de imagens (lado direito)
        images_frame = ttk.Frame(main_frame)
        images_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Imagem original
        original_frame = ttk.LabelFrame(images_frame, text="Imagem Original", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(original_frame, text="Nenhuma imagem carregada")
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        # Imagem corrigida
        corrected_frame = ttk.LabelFrame(images_frame, text="Imagem Corrigida", padding="5")
        corrected_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.corrected_label = ttk.Label(corrected_frame, text="Nenhuma imagem carregada")
        self.corrected_label.pack(fill=tk.BOTH, expand=True)
        
        # Botão de processamento
        ttk.Button(main_frame, text="🔄 Processar Imagem", command=self.process_image).grid(row=2, column=0, pady=(10, 0))
        
    def create_parameter_widgets(self, parent):
        """Cria os widgets de parâmetros editáveis"""
        # FOV
        ttk.Label(parent, text="FOV:").grid(row=0, column=0, sticky=tk.W, pady=2)
        fov_entry = ttk.Entry(parent, textvariable=self.fov_var, width=10)
        fov_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # PFOV
        ttk.Label(parent, text="PFOV:").grid(row=1, column=0, sticky=tk.W, pady=2)
        pfov_entry = ttk.Entry(parent, textvariable=self.pfov_var, width=10)
        pfov_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # X center
        ttk.Label(parent, text="X center:").grid(row=2, column=0, sticky=tk.W, pady=2)
        xcenter_entry = ttk.Entry(parent, textvariable=self.xcenter_var, width=10)
        xcenter_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Y center
        ttk.Label(parent, text="Y center:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ycenter_entry = ttk.Entry(parent, textvariable=self.ycenter_var, width=10)
        ycenter_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Radius
        ttk.Label(parent, text="Radius:").grid(row=4, column=0, sticky=tk.W, pady=2)
        radius_entry = ttk.Entry(parent, textvariable=self.radius_var, width=10)
        radius_entry.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Angle
        ttk.Label(parent, text="Angle:").grid(row=5, column=0, sticky=tk.W, pady=2)
        angle_entry = ttk.Entry(parent, textvariable=self.angle_var, width=10)
        angle_entry.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Dtype
        ttk.Label(parent, text="Dtype:").grid(row=6, column=0, sticky=tk.W, pady=2)
        dtype_combo = ttk.Combobox(parent, textvariable=self.dtype_var, 
                                  values=["linear", "equalarea", "orthographic", "stereographic"],
                                  state="readonly", width=10)
        dtype_combo.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Format
        ttk.Label(parent, text="Format:").grid(row=7, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(parent, textvariable=self.format_var,
                                   values=["fullframe", "circular"],
                                   state="readonly", width=10)
        format_combo.grid(row=7, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Pad
        ttk.Label(parent, text="Pad:").grid(row=8, column=0, sticky=tk.W, pady=2)
        pad_entry = ttk.Entry(parent, textvariable=self.pad_var, width=10)
        pad_entry.grid(row=8, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Bind events para atualização automática
        for widget in [fov_entry, pfov_entry, xcenter_entry, ycenter_entry, 
                      radius_entry, angle_entry, dtype_combo, format_combo, pad_entry]:
            widget.bind('<KeyRelease>', lambda e: self.process_image())
            widget.bind('<<ComboboxSelected>>', lambda e: self.process_image())
        
    def open_image(self):
        """Abre uma imagem"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.original_image_path = file_path
            self.load_and_display_original()
            self.process_image()
    
    def load_and_display_original(self):
        """Carrega e exibe a imagem original"""
        if self.original_image_path:
            # Carrega a imagem
            image = Image.open(self.original_image_path)
            
            # Redimensiona para exibição mantendo proporção
            display_size = (400, 400)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Cria uma nova imagem com fundo branco para centralizar
            display_img = Image.new('RGB', display_size, (255, 255, 255))
            x_offset = (display_size[0] - image.size[0]) // 2
            y_offset = (display_size[1] - image.size[1]) // 2
            display_img.paste(image, (x_offset, y_offset))
            
            # Converte para PhotoImage
            self.original_photo = ImageTk.PhotoImage(display_img)
            self.original_label.configure(image=self.original_photo, text="")
    
    def process_image(self):
        """Processa a imagem com os parâmetros atuais"""
        if not self.original_image_path:
            return
            
        try:
            # Prepara os parâmetros
            params = {
                "fov": self.fov_var.get(),
                "pfov": self.pfov_var.get(),
                "xcenter": self.xcenter_var.get() if self.xcenter_var.get() != -1 else None,
                "ycenter": self.ycenter_var.get() if self.ycenter_var.get() != -1 else None,
                "radius": self.radius_var.get() if self.radius_var.get() != -1 else None,
                "pad": self.pad_var.get(),
                "angle": self.angle_var.get() if self.angle_var.get() != -1 else None,
                "dtype": self.dtype_var.get(),
                "format": self.format_var.get()
            }
            
            # Aplica a correção
            defisheye = DefisheyeAlgorithm(self.original_image_path, **params)
            corrected_cv = defisheye.convert()
            
            # Converte de BGR para RGB
            corrected_rgb = cv2.cvtColor(corrected_cv, cv2.COLOR_BGR2RGB)
            
            # Converte para PIL
            corrected_pil = Image.fromarray(corrected_rgb)
            
            # Redimensiona para exibição mantendo proporção
            display_size = (400, 400)
            corrected_pil.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Cria uma nova imagem com fundo branco para centralizar
            display_img = Image.new('RGB', display_size, (255, 255, 255))
            x_offset = (display_size[0] - corrected_pil.size[0]) // 2
            y_offset = (display_size[1] - corrected_pil.size[1]) // 2
            display_img.paste(corrected_pil, (x_offset, y_offset))
            
            # Converte para PhotoImage
            self.corrected_photo = ImageTk.PhotoImage(display_img)
            self.corrected_label.configure(image=self.corrected_photo, text="")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar imagem: {str(e)}")
            print(f"Erro detalhado: {e}")
    
    def apply_preset(self, event=None):
        """Aplica um preset selecionado"""
        preset_name = self.preset_var.get()
        try:
            if preset_name == "stereographic":
                self.fov_var.set(180)
                self.pfov_var.set(120)
                self.xcenter_var.set(-1)
                self.ycenter_var.set(-1)
                self.radius_var.set(-1)
                self.angle_var.set(0)
                self.dtype_var.set("stereographic")
                self.format_var.set("fullframe")
                self.pad_var.set(0)
            elif preset_name == "linear":
                self.fov_var.set(180)
                self.pfov_var.set(120)
                self.xcenter_var.set(-1)
                self.ycenter_var.set(-1)
                self.radius_var.set(-1)
                self.angle_var.set(0)
                self.dtype_var.set("linear")
                self.format_var.set("fullframe")
                self.pad_var.set(0)
            elif preset_name == "equalarea":
                self.fov_var.set(180)
                self.pfov_var.set(120)
                self.xcenter_var.set(-1)
                self.ycenter_var.set(-1)
                self.radius_var.set(-1)
                self.angle_var.set(0)
                self.dtype_var.set("equalarea")
                self.format_var.set("fullframe")
                self.pad_var.set(0)
            elif preset_name == "orthographic":
                self.fov_var.set(180)
                self.pfov_var.set(120)
                self.xcenter_var.set(-1)
                self.ycenter_var.set(-1)
                self.radius_var.set(-1)
                self.angle_var.set(0)
                self.dtype_var.set("orthographic")
                self.format_var.set("fullframe")
                self.pad_var.set(0)
            
            # Processa a imagem com os novos parâmetros
            self.process_image()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar preset: {str(e)}")
    
    def show_preset_info(self):
        """Mostra informações sobre o preset atual"""
        preset_name = self.preset_var.get()
        try:
            message = f"Preset: {preset_name}\n\n"
            
            if preset_name == "stereographic":
                message += "Descrição: Projeção estereográfica - mantém ângulos e distâncias\n"
                message += "Melhor para: Fotografia geral, arquitetura\n"
            elif preset_name == "linear":
                message += "Descrição: Projeção linear - mantém linhas retas\n"
                message += "Melhor para: Documentação técnica, medições\n"
            elif preset_name == "equalarea":
                message += "Descrição: Projeção de área igual - mantém proporções de área\n"
                message += "Melhor para: Análise espacial, mapeamento\n"
            elif preset_name == "orthographic":
                message += "Descrição: Projeção ortográfica - vista paralela\n"
                message += "Melhor para: Visualização 3D, simulações\n"
            
            message += "\nParâmetros atuais:\n"
            message += f"FOV: {self.fov_var.get()}°\n"
            message += f"PFOV: {self.pfov_var.get()}°\n"
            message += f"X center: {self.xcenter_var.get()}\n"
            message += f"Y center: {self.ycenter_var.get()}\n"
            message += f"Radius: {self.radius_var.get()}\n"
            message += f"Angle: {self.angle_var.get()}°\n"
            message += f"Dtype: {self.dtype_var.get()}\n"
            message += f"Format: {self.format_var.get()}\n"
            message += f"Pad: {self.pad_var.get()}\n"
            
            messagebox.showinfo("Informações do Preset", message)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter informações do preset: {str(e)}")
    
    def save_result(self):
        """Salva o resultado processado"""
        if not self.original_image_path:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvar Imagem Corrigida",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Prepara os parâmetros para salvar
                params = {
                    "fov": self.fov_var.get(),
                    "pfov": self.pfov_var.get(),
                    "xcenter": self.xcenter_var.get() if self.xcenter_var.get() != -1 else None,
                    "ycenter": self.ycenter_var.get() if self.ycenter_var.get() != -1 else None,
                    "radius": self.radius_var.get() if self.radius_var.get() != -1 else None,
                    "pad": self.pad_var.get(),
                    "angle": self.angle_var.get() if self.angle_var.get() != -1 else None,
                    "dtype": self.dtype_var.get(),
                    "format": self.format_var.get()
                }
                
                # Valida parâmetros
                errors = validate_params(params)
                if errors:
                    error_message = "Erros de validação:\n" + "\n".join(errors)
                    messagebox.showerror("Erro de Validação", error_message)
                    return
                
                defisheye = DefisheyeAlgorithm(self.original_image_path, **params)
                defisheye.convert(outfile=file_path)
                
                messagebox.showinfo("Sucesso", f"Imagem salva em: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar imagem: {str(e)}")
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()


if __name__ == "__main__":
    app = IntegratedDefisheyeApp()
    app.run()
