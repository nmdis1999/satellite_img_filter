import type { NextApiRequest, NextApiResponse } from 'next'
import { spawn } from 'child_process'
import path from 'path'
import { homedir } from 'os'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    // Get path to the Python script
    const scriptPath = path.join(homedir(), 'ef_hackathon', 'simulator.py')
    console.log('Script path:', scriptPath)

    // Format the payload as expected by the Python script
    const payload = {
      user_id: "user123",
      data: {
        query: {
          location: req.body.location,
          start_time: req.body.startTime,
          end_time: req.body.endTime,
        },
        timestamp: new Date().toISOString(),
      },
    }

    console.log('Sending payload:', JSON.stringify(payload, null, 2))

    // Spawn Python process
    const python = spawn('python3', [scriptPath])
    let dataString = ''
    let errorString = ''

    // Send payload to Python script
    python.stdin.write(JSON.stringify(payload))
    python.stdin.end()

    // Collect data from script
    python.stdout.on('data', (data) => {
      dataString += data.toString()
      console.log('Python output:', data.toString())
    })

    // Collect errors
    python.stderr.on('data', (data) => {
      errorString += data.toString()
      console.error('Python error:', data.toString())
    })

    // Handle completion
    const response = await new Promise((resolve, reject) => {
      python.on('close', (code) => {
        console.log('Python process exited with code', code)
        if (code !== 0) {
          reject(new Error(`Python script exited with code ${code}. Error: ${errorString}`))
          return
        }
        try {
          const jsonData = JSON.parse(dataString)
          resolve(jsonData)
        } catch (e) {
          console.error('Failed to parse Python output:', dataString)
          reject(new Error('Failed to parse Python script output'))
        }
      })
    })

    res.status(200).json(response)
  } catch (error: any) {
    console.error('API Error:', error)
    res.status(500).json({ 
      status: 'error',
      message: error.message || 'Internal server error',
      details: error.toString()
    })
  }
}
