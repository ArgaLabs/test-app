export default function Home() {
  return (
    <div className="py-16 text-center space-y-6">
      <h1 className="text-4xl font-bold">Unified File Manager</h1>
      <p className="text-gray-600 max-w-xl mx-auto">
        Connect Dropbox, Box, and Google Drive. Manage files across all platforms,
        parse documents with Unstructured, and manage your Google Calendar — all
        from one place. Slack notifications keep your team in the loop.
      </p>
      <div className="flex gap-4 justify-center mt-8">
        <a
          href="/connections"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Connect Accounts
        </a>
        <a
          href="/files"
          className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300"
        >
          Browse Files
        </a>
      </div>
    </div>
  );
}
