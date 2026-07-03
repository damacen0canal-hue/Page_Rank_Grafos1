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
        pr = nx.pagerank(G, weight='weight')
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
