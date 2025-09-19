
import { Page } from '../types';

export const generatePdf = async (pages: Page[], theme: string): Promise<void> => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const a4Width = 210;
  const a4Height = 297;
  
  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const element = document.getElementById(page.id);
    if (!element) {
        console.error(`Element with id ${page.id} not found`);
        continue;
    }

    if (i > 0) {
      doc.addPage();
    }
    
    // Temporarily make element visible for rendering
    element.style.display = 'block';
    
    const canvas = await window.html2canvas(element, {
      scale: 2, // Increase resolution
      useCORS: true,
      backgroundColor: '#ffffff',
    });

    element.style.display = 'none';

    const imgData = canvas.toDataURL('image/png');
    doc.addImage(imgData, 'PNG', 0, 0, a4Width, a4Height);
  }

  doc.save(`${theme.replace(/ /g, '_')}_coloring_page.pdf`);
};
