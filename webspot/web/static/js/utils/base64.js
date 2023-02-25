const {btoa, encode} = Base64;

export const convertToBase64 = (htmlContent) => {
  return encode(htmlContent);
};
