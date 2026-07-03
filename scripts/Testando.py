import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import copy

class PageRankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PageRank Simulator")
        self.geometry("800x600")
        
        # Estado matemático da rede
        self.nodes = {}  # Formato: {id: {'name': str, 'x': int, 'y': int}}
        self.edges = {}  # Formato: {(id_origem, id_destino): peso}
        self.history = [] # Memória de Undo (5 passos)
        
        self.mode = None
        self.node_id = 1
        self.drag_item = None
        self.connect_src = None
        
        # Interface Gráfica
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, 'drag_item', None))
        
        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Botões
        botoes = [("CREATE", "create"), ("CONNECT", "connect"), ("MODIFY", "modify")]
        for texto, modo in botoes:
            tk.Button(toolbar, text=texto, command=lambda m=modo: self.set_mode(m)).pack(side=tk.LEFT, padx=5)
            
        tk.Button(toolbar, text="UNDO", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="PAGE-RANK IT", command=self.calcular_pagerank, bg="lightgreen").pack(side=tk.RIGHT, padx=5)
        
        self.lbl_mode = tk.Label(toolbar, text="Modo: SELEÇÃO", fg="blue", font=("Arial", 10, "bold"))
        self.lbl_mode.pack(side=tk.RIGHT, padx=20)

    def save_state(self):
        # Salva o estado atual na memória limitando a 5 passos
        self.history.append((copy.deepcopy(self.nodes), copy.deepcopy(self.edges)))
        self.history = self.history[-5:]

    def undo(self):
        if self.history:
            self.nodes, self.edges = self.history.pop()
            self.redraw()

    def set_mode(self, mode):
        self.mode = mode
        self.connect_src = None
        self.lbl_mode.config(text=f"Modo: {mode.upper()}")
        
        if mode == "create":
            self.save_state() # Salva histórico estrutural
            # Posição escalonada simples para evitar sobreposição
            x, y = 100 + (self.node_id * 40 % 500), 100 + (self.node_id * 40 % 400)
            self.nodes[self.node_id] = {'name': f"Nó {self.node_id}", 'x': x, 'y': y}
            self.node_id += 1
            self.redraw()
            self.set_mode("seleção") # Volta pro modo neutro após criar

    def redraw(self):
        self.canvas.delete("all")
        # Desenha as setas (edges) e os pesos no meio delas
        for (u, v), w in self.edges.items():
            x1, y1 = self.nodes[u]['x'], self.nodes[u]['y']
            x2, y2 = self.nodes[v]['x'], self.nodes[v]['y']
            
            # Matemática para encurtar a linha em 25px (raio do nó) para a seta aparecer antes do círculo
            dx, dy = x2 - x1, y2 - y1
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                x2_arr = x2 - (dx/dist) * 25
                y2_arr = y2 - (dy/dist) * 25
            else:
                x2_arr, y2_arr = x2, y2
                
            # Desenhando a linha com a seta um pouco maior (arrowshape)
            self.canvas.create_line(x1, y1, x2_arr, y2_arr, arrow=tk.LAST, arrowshape=(15, 20, 5), width=2, fill="gray")
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2 - 10, text=str(w), fill="red", font=("Arial", 10, "bold"))
            
        # Desenha os nós (nodes)
        for nid, data in self.nodes.items():
            x, y = data['x'], data['y']
            self.canvas.create_oval(x-25, y-25, x+25, y+25, fill="lightblue")
            self.canvas.create_text(x, y, text=data['name'])

    def get_item_at(self, x, y):
        # Verifica se clicou em um nó
        for nid, d in self.nodes.items():
            if (d['x']-25 <= x <= d['x']+25) and (d['y']-25 <= y <= d['y']+25):
                return "node", nid
        # Verifica se clicou no meio da seta (para editar peso)
        for (u, v) in self.edges:
            mx, my = (self.nodes[u]['x'] + self.nodes[v]['x'])/2, (self.nodes[u]['y'] + self.nodes[v]['y'])/2
            if abs(mx - x) < 20 and abs(my - y) < 20:
                return "edge", (u, v)
        return None, None

    def on_click(self, event):
        tipo, item_id = self.get_item_at(event.x, event.y)
        
        if tipo == "node":
            self.drag_item = item_id
            
            if self.mode == "connect":
                if not self.connect_src:
                    self.connect_src = item_id # Marca o primeiro nó
                elif self.connect_src != item_id:
                    self.save_state()
                    dir_menu = simpledialog.askstring("Direção", "Digite:\n1 -> Ida\n2 <- Volta\n3 <-> Dupla")
                    if dir_menu == "1": self.edges[(self.connect_src, item_id)] = 1.0
                    elif dir_menu == "2": self.edges[(item_id, self.connect_src)] = 1.0
                    elif dir_menu == "3":
                        self.edges[(self.connect_src, item_id)] = 1.0
                        self.edges[(item_id, self.connect_src)] = 1.0
                    self.set_mode("seleção")
                    self.redraw()
                    
            elif self.mode == "modify":
                self.save_state()
                novo_nome = simpledialog.askstring("Modificar Nó", "Novo nome:", initialvalue=self.nodes[item_id]['name'])
                if novo_nome: self.nodes[item_id]['name'] = novo_nome
                self.set_mode("seleção")
                self.redraw()
                
        elif tipo == "edge" and self.mode == "modify":
            self.save_state()
            novo_peso = simpledialog.askfloat("Modificar Seta", "Novo peso:", initialvalue=self.edges[item_id])
            if novo_peso is not None: self.edges[item_id] = novo_peso
            self.set_mode("seleção")
            self.redraw()

    def on_drag(self, event):
        # Arrastar não salva no histórico (mudança apenas estética)
        if self.drag_item and self.mode != "connect":
            self.nodes[self.drag_item]['x'] = event.x
            self.nodes[self.drag_item]['y'] = event.y
            self.redraw()

    def calcular_pagerank(self):
        G = nx.DiGraph()
        # Adiciona nós e setas no NetworkX
        for nid, d in self.nodes.items(): 
            G.add_node(d['name'])
        for (u, v), w in self.edges.items(): 
            G.add_edge(self.nodes[u]['name'], self.nodes[v]['name'], weight=w)
            
        if not G.nodes: 
            return messagebox.showwarning("Aviso", "Crie pelo menos um nó!")
            
        # Calcula o ranking
        pr = nx.pagerank(G, weight='weight', tol=0.0001, max_iter=100)
        ranking = "\n".join([f"{i+1}º - {k}: {v:.4f}" for i, (k, v) in enumerate(sorted(pr.items(), key=lambda x: x[1], reverse=True))])
        
        # Cria uma nova janela limpa com os resultados (estilo aba)
        nova_janela = tk.Toplevel(self)
        nova_janela.title("Resultado do PageRank")
        nova_janela.geometry("350x450")
        
        titulo = tk.Label(nova_janela, text="Ranking Final", font=("Arial", 14, "bold"))
        titulo.pack(pady=10)
        
        texto_resultado = tk.Text(nova_janela, font=("Arial", 12), bg="#f0f0f0", relief=tk.FLAT)
        texto_resultado.insert(tk.END, ranking)
        texto_resultado.config(state=tk.DISABLED) # Impede edição do texto
        texto_resultado.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

if __name__ == "__main__":
    app = PageRankApp()
    app.mainloop()