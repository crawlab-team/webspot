const {createStore} = Vuex;

const store = createStore({
  state() {
    return {
      requests: [],
      activeRequestId: undefined,
      isLoading: false,
      requestForm: {},
    };
  },
  getters: {
    isEmpty(state) {
      return state.requests.length === 0;
    },
    activeRequest(state) {
      return state.requests.find((request) => request._id === state.activeRequestId);
    },
    activeRequestStatus(state, getters) {
      return getters.activeRequest ? getters.activeRequest.status : '';
    },
    activeRequestResults(state, getters) {
      return getters.activeRequest ? getters.activeRequest.results : [];
    },
    activeRequestHtml(state, getters) {
      return getters.activeRequest ? getters.activeRequest.html : '';
    },
    activeRequestHtmlHighlighted(state, getters) {
      return getters.activeRequest ? getters.activeRequest.html_highlighted : '';
    },
    activeRequestFormattedError(state, getters) {
      if (!getters.activeRequest) return '';
      if (!getters.activeRequest.error) return '';
      return getters.activeRequest.error.split('\n').join('<br>');
    },
    setRequestForm(state, requestForm) {
      state.requestForm = requestForm;
    },
    resetRequestForm(state) {
      state.requestForm = {};
    },
  },
  mutations: {
    setRequests(state, requests) {
      state.requests = requests;
    },
    setActiveRequestId(state, id) {
      state.activeRequestId = id;
    },
    setIsLoading(state, isLoading) {
      state.isLoading = isLoading;
    }
  },
  actions: {
    async getRequests({commit, state}) {
      const res = await axios.get(`/api/requests`);
      if (JSON.stringify(res.data) === JSON.stringify(state.requests)) {
        return;
      }
      commit('setRequests', res.data);

      // Set active request id if it's not set yet
      if (state.activeRequestId === undefined && res.data.length > 0) {
        commit('setActiveRequestId', res.data[0]._id);
      }
    },
    async postRequest({commit, dispatch}, request) {
      const res = await axios.post(`/api/requests`, {...request});
      await dispatch('getRequests');

      // Set result id as active
      commit('setActiveRequestId', res.data._id);
    },
  }
});

export default store;
