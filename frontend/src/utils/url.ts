export const getDomainFromUrl = (url: string): string => {
    try {
      const parsedUrl = new URL(url);
      return parsedUrl.hostname;    // KEEP www. prefix if present
    } catch (error) {
      return url;   // fallback
    }
  };