function ajustarAlturaIframe() {
    const iframe = document.getElementById("orcamento-frame");
    if (iframe && iframe.contentWindow && iframe.contentDocument.body) {
      pixels = iframe.contentDocument.body.scrollHeight + 57;
      iframe.style.height = pixels + "px";
      console.log("Altura do iframe ajustada para: " + pixels + "px");
    }
  }

  function paginarConteudo(rootElement, alturaMax = 1122) {
    const originalChildren = Array.from(rootElement.children);
    let currentPagina = document.createElement('div');
    currentPagina.className = 'pagina';
    rootElement.innerHTML = '';
    rootElement.appendChild(currentPagina);

    originalChildren.forEach(child => {
      currentPagina.appendChild(child);
      if (currentPagina.scrollHeight > alturaMax) {
        currentPagina.removeChild(child);
        currentPagina = document.createElement('div');
        currentPagina.className = 'pagina';
        rootElement.appendChild(currentPagina);
        currentPagina.appendChild(child);
      }
    });
  }

  document.getElementById("orcamento-frame").onload = () => {
    const iframe = document.getElementById('orcamento-frame');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    const style = doc.createElement('style');
    style.innerHTML = `
      .pagina {
        width: 100%;
        max-height: 1122px;
        overflow: hidden;
        page-break-after: always;
      }
    `;
    doc.head.appendChild(style);

    const conteudo = doc.getElementById('conteudo-orcamento');
    if (conteudo) {
      paginarConteudo(conteudo);
      ajustarAlturaIframe();
    } else {
      console.warn("Elemento com id 'conteudo-orcamento' não encontrado.");
    }
  };

  window.addEventListener('load', function () {
    const { jsPDF } = window.jspdf;

    document.getElementById('download-pdf').addEventListener('click', async function () {
      const btn = this;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Gerando PDF...';
      btn.disabled = true;

      try {
        const iframe = document.getElementById('orcamento-frame');
        const doc = iframe.contentDocument || iframe.contentWindow.document;

        await convertImagesToBase64(doc);
        await new Promise(r => setTimeout(r, 300));

        const options = {
          scale: 0.5,
          useCORS: true,
          backgroundColor: null,
          onclone: cloned => {
            cloned.body.style.margin = '0';
            cloned.body.style.padding = '0';
            cloned.documentElement.style.margin = '0 auto';
            cloned.documentElement.style.padding = '0px';
            cloned.documentElement.scrollTop = 0;
            cloned.body.scrollTop = 0;
          }
        };

        const canvas = await html2canvas(doc.body, options);
        const img = canvas.toDataURL('image/png');

        const pdf = new jsPDF('p', 'mm', 'a4');
        const pw = pdf.internal.pageSize.getWidth();
        const ph = pdf.internal.pageSize.getHeight();
        const ih = (canvas.height * pw) / canvas.width;
        let heightLeft = ih, position = 0;

        pdf.addImage(img, 'PNG', 0, position, pw, ih);
        heightLeft -= ph;

        while (heightLeft > 0) {
          position = heightLeft - ih;
          pdf.addPage();
          pdf.addImage(img, 'PNG', 0, position, pw, ih);
          heightLeft -= ph;
        }

        pdf.save('orcamento.pdf');
      } catch (e) {
        console.error('Erro:', e);
        alert('Erro ao gerar PDF: ' + e.message);
      } finally {
        btn.innerHTML = 'Baixar PDF';
        btn.disabled = false;
      }
    });

    async function convertImagesToBase64(document) {
      const imgs = document.querySelectorAll('img');
      await Promise.all([...imgs].map(img => {
        if (img.src.startsWith('data:')) return Promise.resolve();
        return fetch(img.src, { mode: 'cors', credentials: 'include' })
          .then(res => res.blob())
          .then(blob => new Promise(res => {
            const r = new FileReader();
            r.onloadend = () => {
              img.src = r.result;
              res();
            };
            r.readAsDataURL(blob);
          }))
          .catch(err => console.warn('Img base64 fail', img.src, err));
      }));
    }
  });
  function download() {
    const iframe = document.getElementById('orcamento-frame');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    
  
    if (!content) {
      alert("Conteúdo não encontrado para gerar o PDF.");
      return;
    }
  
    const container = document.getElementById('print-container');
    container.innerHTML = content.outerHTML;
  
    const opt = {
      margin: 0,
      filename: 'orcamento.pdf',
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
  
    html2pdf().set(opt).from(container).save();
  }
  