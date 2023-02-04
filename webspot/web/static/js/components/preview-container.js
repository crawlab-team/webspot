export default {
  name: 'PreviewContainer',
  props: {
    html: String,
  },
  template: `<div class="preview-container">
  <iframe id="iframe" width="100%" height="100%" :src="'data:text/html;base64,' + html"></iframe>
</div>`
};
