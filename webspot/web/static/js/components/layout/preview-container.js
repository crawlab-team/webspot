const {ref, computed, watch, onMounted} = Vue;
const {useStore} = Vuex;
const {ElMessageBox} = ElementPlus;

export default {
  name: 'PreviewContainer',
  setup() {
    const store = useStore();

    const activeRequestId = computed(() => store.state.activeRequestId);

    const previewMode = computed(() => store.getters.previewMode);

    const activeRequestHtmlSrc = computed(() => `/api/requests/${activeRequestId.value}/html?mode=${previewMode.value}`);

    const isLoading = ref(false);

    const invokeLoading = () => {
      isLoading.value = true;
      setTimeout(() => {
        isLoading.value = false;
      }, 1000);
    };

    watch(() => activeRequestId.value, invokeLoading);
    onMounted(invokeLoading);

    window.addEventListener('message', async (event) => {
      const nodeId = event.data;
      const res = await axios.get(`/api/requests/${activeRequestId.value}/nodes/${nodeId}`);
      console.debug(res.data);
      // await ElMessageBox.alert(event.data)
      // console.debug(event.data);
    }, false);

    return {
      activeRequestHtmlSrc,
      isLoading,
    };
  },
  template: `<div class="preview-container">
  <el-skeleton v-if="isLoading" style="height: 100%; width: 100%; padding: 2%" :rows="25"/>
  <iframe v-else id="iframe" width="100%" height="100%" :src="activeRequestHtmlSrc"></iframe>
</div>`
};
