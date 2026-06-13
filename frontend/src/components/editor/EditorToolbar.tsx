import type { Editor } from '@tiptap/react'

function Btn({
  active,
  onClick,
  title,
  children,
  disabled,
}: {
  active?: boolean
  onClick: () => void
  title: string
  children: React.ReactNode
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      className={`rte-tool${active ? ' rte-tool--active' : ''}`}
      title={title}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}

const Sep = () => <span className="rte-sep" />

export function EditorToolbar({ editor, onInsertImage }: { editor: Editor | null; onInsertImage?: () => void }) {
  if (!editor) return null
  const setLink = () => {
    const prev = editor.getAttributes('link').href as string | undefined
    const url = window.prompt('Link URL', prev ?? 'https://')
    if (url === null) return
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run()
      return
    }
    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }

  return (
    <div className="rte-toolbar">
      <Btn title="Bold (Ctrl+B)" active={editor.isActive('bold')} onClick={() => editor.chain().focus().toggleBold().run()}>
        <b>B</b>
      </Btn>
      <Btn title="Italic (Ctrl+I)" active={editor.isActive('italic')} onClick={() => editor.chain().focus().toggleItalic().run()}>
        <i>I</i>
      </Btn>
      <Btn title="Underline (Ctrl+U)" active={editor.isActive('underline')} onClick={() => editor.chain().focus().toggleUnderline().run()}>
        <u>U</u>
      </Btn>
      <Btn title="Strikethrough" active={editor.isActive('strike')} onClick={() => editor.chain().focus().toggleStrike().run()}>
        <s>S</s>
      </Btn>
      <Sep />
      <Btn title="Heading 2" active={editor.isActive('heading', { level: 2 })} onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>
        H2
      </Btn>
      <Btn title="Heading 3" active={editor.isActive('heading', { level: 3 })} onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}>
        H3
      </Btn>
      <Btn title="Paragraph" active={editor.isActive('paragraph')} onClick={() => editor.chain().focus().setParagraph().run()}>
        ¶
      </Btn>
      <Sep />
      <Btn title="Bullet list" active={editor.isActive('bulletList')} onClick={() => editor.chain().focus().toggleBulletList().run()}>
        • —
      </Btn>
      <Btn title="Numbered list" active={editor.isActive('orderedList')} onClick={() => editor.chain().focus().toggleOrderedList().run()}>
        1.
      </Btn>
      <Btn title="Quote" active={editor.isActive('blockquote')} onClick={() => editor.chain().focus().toggleBlockquote().run()}>
        ❝
      </Btn>
      <Btn title="Divider" onClick={() => editor.chain().focus().setHorizontalRule().run()}>
        —
      </Btn>
      <Sep />
      <Btn title="Align left" active={editor.isActive({ textAlign: 'left' })} onClick={() => editor.chain().focus().setTextAlign('left').run()}>
        ⯇
      </Btn>
      <Btn title="Align center" active={editor.isActive({ textAlign: 'center' })} onClick={() => editor.chain().focus().setTextAlign('center').run()}>
        ☰
      </Btn>
      <Btn title="Align right" active={editor.isActive({ textAlign: 'right' })} onClick={() => editor.chain().focus().setTextAlign('right').run()}>
        ⯈
      </Btn>
      <Btn title="Justify" active={editor.isActive({ textAlign: 'justify' })} onClick={() => editor.chain().focus().setTextAlign('justify').run()}>
        ▤
      </Btn>
      <Sep />
      <Btn title="Link" active={editor.isActive('link')} onClick={setLink}>
        🔗
      </Btn>
      {onInsertImage && (
        <Btn title="Insert image" onClick={onInsertImage}>
          🖼
        </Btn>
      )}
      <Btn title="Clear formatting" onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}>
        ⌫
      </Btn>
    </div>
  )
}
