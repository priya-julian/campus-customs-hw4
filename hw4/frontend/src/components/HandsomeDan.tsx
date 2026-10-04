/**
 * Handsome Dan, the Campus Customs mascot — built in HTML and CSS, no image file.
 *
 * Everything scales from the `size` prop via a CSS custom property, so the same markup
 * works as a 30px chat avatar and as a 90px greeter in the panel header.
 */
export default function HandsomeDan({
  size = 40,
  talking = false,
}: {
  size?: number
  talking?: boolean
}) {
  return (
    <span
      className={talking ? 'dan talking' : 'dan'}
      style={{ ['--dan' as string]: `${size}px` }}
      role="img"
      aria-label="Handsome Dan, the Campus Customs bulldog"
    >
      <span className="dan-ear left" />
      <span className="dan-ear right" />
      <span className="dan-head">
        <span className="dan-brow left" />
        <span className="dan-brow right" />
        <span className="dan-eye left" />
        <span className="dan-eye right" />
        <span className="dan-muzzle">
          <span className="dan-nose" />
          <span className="dan-lip" />
          <span className="dan-tongue" />
        </span>
      </span>
      <span className="dan-collar">
        <span className="dan-tag" />
      </span>
    </span>
  )
}
