# Accessibility

The project aims to follow WCAG 2.2 AA where Streamlit permits it.

Current measures include:

- Descriptive text labels for search, navigation, source, download, and summary controls.
- Text-labelled controls for hiding saved/seen papers and explicitly changing seen state.
- Safety messages that use text rather than color alone.
- Heading-based paper and section structure.
- Original abstracts and source links kept adjacent to generated explanations.
- A tabular alternative to the publication trend chart.
- A tabular Evidence Explorer comparison with source passages available as ordinary text.
- Keyboard-operable controls supplied by Streamlit.
- English and Norwegian interface labels.

Before release, manually test keyboard navigation, focus visibility, browser zoom at 200%, narrow mobile layouts, and a screen reader. Automated tests do not replace this review.

## v0.4 Manual Checks

- The search form, local reading filters, tabs, and paper-card actions were checked in an emulated 390 x 844 mobile viewport.
- Controls wrapped or stacked without text overlap, and the tab row remained horizontally navigable.
- A physical phone, browser zoom at 200%, full keyboard pass, and screen-reader pass remain to be completed before calling the accessibility review comprehensive.

Accessibility issues are welcome as GitHub issues and should not contain personal medical information.
