import { useNuxtApp } from "#imports";

export function useAxiosDownloader() {
  const { $axios } = useNuxtApp();

  function download(url: string, filename: string) {
    $axios({
      url,
      method: "GET",
      responseType: "blob",
    }).then((response: { data: BlobPart; }) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    });
  }

  return download;
}
