import Image from '@tiptap/extension-image'
import { ReactNodeViewRenderer } from '@tiptap/react'
import { BusinessPlanImageNodeView } from '../BusinessPlanImageNodeView'

/**
 * Inline rich-text image node — the single source of truth for image placement.
 * Extends the TipTap Image node with business-plan attributes that round-trip
 * through HTML as data-* attributes, so the same content drives the editor,
 * preview, and the Word/PDF report generators.
 */
export const BusinessPlanImage = Image.extend({
  draggable: true,

  addAttributes() {
    return {
      ...this.parent?.(),
      imageId: {
        default: null,
        parseHTML: (el) => el.getAttribute('data-image-id'),
        renderHTML: (attrs) => (attrs.imageId ? { 'data-image-id': attrs.imageId } : {}),
      },
      caption: {
        default: '',
        parseHTML: (el) => el.getAttribute('data-caption') || '',
        renderHTML: (attrs) => ({ 'data-caption': attrs.caption || '' }),
      },
      alignment: {
        default: 'center',
        parseHTML: (el) => el.getAttribute('data-alignment') || 'center',
        renderHTML: (attrs) => ({ 'data-alignment': attrs.alignment || 'center' }),
      },
      widthPercentage: {
        default: 80,
        parseHTML: (el) => Number(el.getAttribute('data-width')) || 80,
        renderHTML: (attrs) => ({ 'data-width': String(attrs.widthPercentage || 80) }),
      },
    }
  },

  addNodeView() {
    return ReactNodeViewRenderer(BusinessPlanImageNodeView)
  },
})
