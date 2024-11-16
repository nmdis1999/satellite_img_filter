import { Card } from "@/components/ui/card";
import { format } from "date-fns";

interface SatelliteData {
  capture_timestamp: string;
  data_url: string;
  location: string;
}

interface QueryResponse {
  status: string;
  source: string;
  request_timestamp: string;
  results: SatelliteData[];
}

interface DataDisplayProps {
  data: QueryResponse;
}

const DataDisplay = ({ data }: DataDisplayProps) => {
  return (
    <div className="mt-8 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-space-800/50 border-space-600 p-4">
          <h3 className="text-lg font-medium text-space-200 mb-2">Query Info</h3>
          <div className="space-y-2">
            <p className="text-sm">
              <span className="text-space-300">Status:</span>{" "}
              <span className="text-green-400">{data.status}</span>
            </p>
            <p className="text-sm">
              <span className="text-space-300">Source:</span>{" "}
              {data.source}
            </p>
            <p className="text-sm">
              <span className="text-space-300">Request Time:</span>{" "}
              {format(new Date(data.request_timestamp), "PPpp")}
            </p>
          </div>
        </Card>

        <Card className="bg-space-800/50 border-space-600 p-4">
          <h3 className="text-lg font-medium text-space-200 mb-2">Results Summary</h3>
          <div className="space-y-2">
            <p className="text-sm">
              <span className="text-space-300">Total Results:</span>{" "}
              {data.results.length}
            </p>
            <p className="text-sm">
              <span className="text-space-300">Latest Capture:</span>{" "}
              {data.results[0] && format(new Date(data.results[0].capture_timestamp), "PPpp")}
            </p>
          </div>
        </Card>
      </div>

      <Card className="bg-space-800/50 border-space-600 p-4">
        <h3 className="text-lg font-medium text-space-200 mb-4">Detailed Results</h3>
        <div className="space-y-4">
          {data.results.map((result, index) => (
            <div
              key={index}
              className="p-3 bg-space-700/50 rounded-lg border border-space-600 hover:border-space-500 transition-colors"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <p className="text-sm">
                  <span className="text-space-300">Time:</span>{" "}
                  {format(new Date(result.capture_timestamp), "PPpp")}
                </p>
                <p className="text-sm">
                  <span className="text-space-300">Location:</span>{" "}
                  {result.location}
                </p>
                <p className="text-sm truncate">
                  <span className="text-space-300">URL:</span>{" "}
                  <a
                    href={result.data_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300"
                  >
                    {result.data_url}
                  </a>
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default DataDisplay;
