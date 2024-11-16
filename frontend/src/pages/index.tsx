import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const locations = [
  "NYC",
  "LA",
  "Chicago",
  "Houston",
  "Miami",
  "Seattle",
  "Boston",
  "Denver",
];

// Inline DataDisplay component
const DataDisplay = ({ data }) => {
  if (!data) return null;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="mt-8 space-y-4">
      <Card className="bg-gray-800 border-gray-700 p-4">
        <h3 className="text-lg font-medium text-gray-300 mb-2">Query Info</h3>
        <div className="space-y-2">
          <p className="text-sm">
            <span className="text-gray-400">Status: </span>
            <span className="text-green-400">{data.status}</span>
          </p>
          <p className="text-sm">
            <span className="text-gray-400">Source: </span>
            <span className="text-white">{data.source}</span>
          </p>
          <p className="text-sm">
            <span className="text-gray-400">Request Time: </span>
            <span className="text-white">{formatDate(data.request_timestamp)}</span>
          </p>
        </div>
      </Card>

      <Card className="bg-gray-800 border-gray-700 p-4">
        <h3 className="text-lg font-medium text-gray-300 mb-2">Results</h3>
        <div className="space-y-4">
          {data.results.map((result, index) => (
            <div
              key={index}
              className="p-3 bg-gray-700 rounded-lg border border-gray-600"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <p className="text-sm">
                  <span className="text-gray-400">Time: </span>
                  <span className="text-white">{formatDate(result.capture_timestamp)}</span>
                </p>
                <p className="text-sm">
                  <span className="text-gray-400">Location: </span>
                  <span className="text-white">{result.location}</span>
                </p>
                <p className="text-sm truncate">
                  <span className="text-gray-400">URL: </span>
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

const Index = () => {
  const { toast } = useToast();
  const [location, setLocation] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

 const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);

  try {
    const startISO = new Date(startTime).toISOString();
    const endISO = new Date(endTime).toISOString();

    const payload = {
      location: location,
      startTime: startISO,
      endTime: endISO,
    };

    console.log('Sending payload:', payload);

    const response = await fetch('/api/satellite-query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error response:', errorData);
      throw new Error(errorData.message || 'Failed to fetch data');
    }

    const result = await response.json();
    console.log('Success response:', result);
    setData(result);
    toast({
      title: "Success!",
      description: "Data fetched successfully",
    });
  } catch (error) {
    console.error('Error:', error);
    toast({
      title: "Error",
      description: error.message || "Failed to fetch satellite data",
      variant: "destructive",
    });
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 animate-float">
            Satellite Data Query System
          </h1>
          <p className="text-gray-300">
            Query satellite data by location and time range
          </p>
        </div>

        <Card className="bg-gray-800 border-gray-700 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Location
                </label>
                <Select
                  value={location}
                  onValueChange={setLocation}
                >
                  <SelectTrigger className="bg-white text-black border-gray-300">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent className="bg-white text-black">
                    {locations.map((loc) => (
                      <SelectItem key={loc} value={loc} className="hover:bg-gray-100">
                        {loc}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Start Time
                </label>
                <Input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="bg-white text-black border-gray-300"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  End Time
                </label>
                <Input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="bg-white text-black border-gray-300"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading || !location || !startTime || !endTime}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Fetching Data...
                </>
              ) : (
                "Query Satellite Data"
              )}
            </Button>
          </form>
        </Card>

        {data && <DataDisplay data={data} />}
      </div>
    </div>
  );
};

export default Index;
