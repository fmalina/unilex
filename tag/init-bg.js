// Listen for any changes to the URL of any tab.
chrome.tabs.onUpdated.addListener(tag.isAllowed);