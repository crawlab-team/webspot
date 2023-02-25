const {ref, computed, watch, onMounted} = Vue;
const {useStore} = Vuex;

export default {
  name: 'PreviewContainer',
  setup() {
    const store = useStore();

    const activeRequestId = computed(() => store.state.activeRequestId);

    const activeRequestHtmlHighlighted = computed(() => {
      const htmlContent = store.getters['activeRequestHtmlHighlighted'];

      // Encode the HTML content to UTF-8
      const utf8Content = new TextEncoder().encode(htmlContent);

      // Convert the UTF-8 content to Base64
      return btoa(String.fromCharCode(...new Uint8Array(utf8Content)));
    });

    const isLoading = ref(false);

    const invokeLoading = () => {
      isLoading.value = true;
      setTimeout(() => {
        isLoading.value = false;
      }, 1000);
    };

    watch(() => activeRequestId.value, invokeLoading);
    onMounted(invokeLoading);

    return {
      activeRequestHtmlHighlighted,
      isLoading,
    };
  },
  template: `<div class="preview-container">
  <el-skeleton v-if="isLoading" style="height: 100%; width: 100%; padding: 2%" :rows="25"/>
  <iframe v-else id="iframe" width="100%" height="100%" :src="'data:text/html;base64,' + activeRequestHtmlHighlighted"></iframe>
</div>`
};
