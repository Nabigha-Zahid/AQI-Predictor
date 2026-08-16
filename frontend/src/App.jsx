import { useEffect, useState } from "react";

import {
  Activity,
  Wind,
  Droplets,
  Gauge,
  Thermometer,
  RefreshCw,
  MapPin,
  Cloud,
  Navigation,
  CalendarDays,
} from "lucide-react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";

const CITIES = [
  "Lahore",
  "Islamabad",
  "Karachi",
];


function getCategory(category) {
  const categories = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
  };

  return categories[category] || "Unknown";
}


function getCategoryClass(category) {
  if (category <= 2) return "good";

  if (category === 3) return "moderate";

  if (category === 4) return "poor";

  return "very-poor";
}


function App() {

  const [selectedCity, setSelectedCity] = useState("Lahore");

  const [data, setData] = useState(null);

  const [cityData, setCityData] = useState({});

  const [forecast, setForecast] = useState([]);

  const [loading, setLoading] = useState(false);

  const [forecastLoading, setForecastLoading] = useState(false);

  const [error, setError] = useState("");


  // --------------------------------------------------
  // FETCH CURRENT CITY DATA
  // --------------------------------------------------

  const fetchCity = async (city) => {

    const response = await fetch(
      `${API_URL}/predict/${city}`
    );

    if (!response.ok) {
      throw new Error(
        `Unable to fetch ${city} data`
      );
    }

    return await response.json();
  };


  // --------------------------------------------------
  // FETCH FORECAST
  // --------------------------------------------------

  const fetchForecast = async (city) => {

    const response = await fetch(
      `${API_URL}/forecast/${city}`
    );

    if (!response.ok) {
      throw new Error(
        `Unable to fetch ${city} forecast`
      );
    }

    return await response.json();
  };


  // --------------------------------------------------
  // FETCH ALL CITIES
  // --------------------------------------------------

  const fetchAllCities = async () => {

    setLoading(true);

    setError("");

    try {

      const results = await Promise.all(
        CITIES.map(async (city) => {

          const result = await fetchCity(city);

          return [city, result];

        })
      );


      const resultObject =
        Object.fromEntries(results);


      setCityData(resultObject);


      setData(
        resultObject[selectedCity]
      );


      // Fetch selected city's forecast
      setForecastLoading(true);

      try {

        const forecastResult =
          await fetchForecast(selectedCity);

        setForecast(
          forecastResult.forecast || []
        );

      } catch (forecastError) {

        console.error(
          "Forecast error:",
          forecastError
        );

        setForecast([]);

      } finally {

        setForecastLoading(false);

      }

    } catch (err) {

      console.error(err);

      setError(
        "Unable to connect to the AQI backend. Make sure FastAPI is running on port 8000."
      );

    } finally {

      setLoading(false);

    }
  };


  // --------------------------------------------------
  // CITY SELECTION
  // --------------------------------------------------

  const selectCity = async (city) => {

    setSelectedCity(city);

    setError("");


    if (cityData[city]) {

      setData(
        cityData[city]
      );

    }


    setForecastLoading(true);


    try {

      const result =
        await fetchForecast(city);

      setForecast(
        result.forecast || []
      );

    } catch (err) {

      console.error(err);

      setForecast([]);

    } finally {

      setForecastLoading(false);

    }

  };


  // --------------------------------------------------
  // INITIAL LOAD
  // --------------------------------------------------

  useEffect(() => {

    fetchAllCities();

  }, []);


  // --------------------------------------------------
  // UPDATE CURRENT DATA WHEN CITY CHANGES
  // --------------------------------------------------

  useEffect(() => {

    if (cityData[selectedCity]) {

      setData(
        cityData[selectedCity]
      );

    }

  }, [selectedCity, cityData]);


  // --------------------------------------------------
  // CHART DATA
  // --------------------------------------------------

  const chartData = data?.pollution
    ? [
        {
          name: "PM2.5",
          value: data.pollution.pm2_5,
        },
        {
          name: "PM10",
          value: data.pollution.pm10,
        },
        {
          name: "CO",
          value: data.pollution.co,
        },
        {
          name: "NO₂",
          value: data.pollution.no2,
        },
        {
          name: "O₃",
          value: data.pollution.o3,
        },
        {
          name: "SO₂",
          value: data.pollution.so2,
        },
      ]
    : [];


  return (

    <div className="app">


      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            <Activity size={24} />
          </div>


          <div>

            <h1>AQI Intelligence</h1>

            <p>
              Air Quality Prediction Platform
            </p>

          </div>

        </div>


        <div className="live-status">

          <span className="live-dot"></span>

          LIVE DATA

        </div>

      </header>



      <main className="container">


        {/* ==================================================
            HERO
        ================================================== */}

        <section className="hero">

          <div className="hero-content">

            <h2 className="hero-title">
              Air Quality{" "}
              <span>Intelligence</span>
            </h2>


            <p className="hero-text">

              Real-time environmental data and
              machine-learning predictions for
              major cities across Pakistan.

            </p>

          </div>


          <div className="city-selector">

            <MapPin size={18} />

            <select
              value={selectedCity}
              onChange={(e) =>
                selectCity(e.target.value)
              }
            >

              {CITIES.map((city) => (

                <option
                  key={city}
                  value={city}
                >
                  {city}
                </option>

              ))}

            </select>

          </div>

        </section>



        {/* ==================================================
            ERROR
        ================================================== */}

        {error && (

          <div className="error-box">

            {error}

          </div>

        )}



        {/* ==================================================
            AQI + MODEL
        ================================================== */}

        <section className="dashboard-grid">


          {/* AQI CARD */}

          <div
            className={`aqi-card ${
              data
                ? getCategoryClass(
                    data.category
                  )
                : ""
            }`}
          >

            <div className="card-top">

              <div>

                <p className="card-label">
                  PREDICTED AIR QUALITY INDEX
                </p>


                <h3>

                  {loading
                    ? "--"
                    : data?.predicted_aqi !==
                      undefined
                    ? Number(
                        data.predicted_aqi
                      ).toFixed(2)
                    : "--"}

                </h3>


                <div className="aqi-status">

                  <span className="status-dot"></span>

                  {data
                    ? getCategory(
                        data.category
                      )
                    : "Loading"}

                </div>


                <div className="aqi-location">

                  <MapPin size={14} />

                  {selectedCity}, Pakistan

                </div>

              </div>


              <div className="aqi-icon">

                <Activity size={30} />

              </div>

            </div>


            <div className="aqi-scale">

              <div className="scale-line"></div>


              <div className="scale-labels">

                <span>GOOD</span>

                <span>FAIR</span>

                <span>MODERATE</span>

                <span>POOR</span>

                <span>VERY POOR</span>

              </div>

            </div>

          </div>



          {/* MODEL INFORMATION */}

          <div className="info-card">

            <div className="info-header">

              <div className="small-icon">

                <Activity size={20} />

              </div>


              <div>

                <p>MODEL INFORMATION</p>

                <strong>
                  Random Forest
                </strong>

              </div>

            </div>


            <div className="model-stat">

              <span>Model Type</span>

              <strong>
                Random Forest
              </strong>

            </div>


            <div className="model-stat">

              <span>Training Data</span>

              <strong>
                12,285 records
              </strong>

            </div>


            <div className="model-stat">

              <span>R² Score</span>

              <strong>
                0.8732
              </strong>

            </div>


            <div className="model-stat">

              <span>Prediction</span>

              <strong>
                Live
              </strong>

            </div>

          </div>

        </section>



        {/* ==================================================
            NEXT 3 DAYS FORECAST
        ================================================== */}

        <section className="section forecast-section">

          <div className="section-title">

            <div className="forecast-heading">

              <CalendarDays size={21} />

              <h3>
                Next 3 Days AQI Forecast
              </h3>

            </div>

          </div>


          <div className="forecast-grid">

            {forecastLoading ? (

              <div className="forecast-loading">

                Loading forecast...

              </div>

            ) : forecast.length > 0 ? (

              forecast.map((item, index) => (

                <div
                  className="forecast-card"
                  key={item.date || index}
                >

                  <div className="forecast-date">

                    <CalendarDays size={17} />

                    <span>
                      {new Date(
                        item.date
                      ).toLocaleDateString(
                        "en-US",
                        {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        }
                      )}
                    </span>

                  </div>


                  <div className="forecast-aqi">

                    {Number(
                      item.predicted_aqi
                    ).toFixed(2)}

                  </div>


                  <div className="forecast-category">

                    <span
                      className={`forecast-dot ${getCategoryClass(
                        item.category
                      )}`}
                    ></span>

                    {getCategory(
                      item.category
                    )}

                  </div>

                </div>

              ))

            ) : (

              <div className="forecast-loading">

                Forecast unavailable.

              </div>

            )}

          </div>

        </section>



        {/* ==================================================
            CURRENT WEATHER
        ================================================== */}

        <section className="section">

          <div className="section-title">

            <h3>
              Current Weather
            </h3>


            <button
              className="refresh-button"
              onClick={fetchAllCities}
              disabled={loading}
            >

              <RefreshCw
                size={15}
                className={
                  loading
                    ? "spin"
                    : ""
                }
              />

              {loading
                ? "Updating..."
                : "Refresh Data"}

            </button>

          </div>


          <div className="stats-grid">


            <div className="stat-card">

              <div className="stat-icon temperature">

                <Thermometer size={20} />

              </div>


              <div>

                <span>
                  Temperature
                </span>

                <strong>

                  {data?.weather?.temperature ??
                    "--"}°C

                </strong>

              </div>

            </div>



            <div className="stat-card">

              <div className="stat-icon humidity">

                <Droplets size={20} />

              </div>


              <div>

                <span>
                  Humidity
                </span>

                <strong>

                  {data?.weather?.humidity ??
                    "--"}%

                </strong>

              </div>

            </div>



            <div className="stat-card">

              <div className="stat-icon pressure">

                <Gauge size={20} />

              </div>


              <div>

                <span>
                  Pressure
                </span>

                <strong>

                  {data?.weather?.pressure ??
                    "--"} hPa

                </strong>

              </div>

            </div>



            <div className="stat-card">

              <div className="stat-icon wind">

                <Wind size={20} />

              </div>


              <div>

                <span>
                  Wind Speed
                </span>

                <strong>

                  {data?.weather?.wind_speed ??
                    "--"} m/s

                </strong>

              </div>

            </div>

          </div>

        </section>



        {/* ==================================================
            POLLUTION
        ================================================== */}

        <section className="section">

          <div className="section-title">

            <h3>
              Pollution Indicators
            </h3>

          </div>


          <div className="pollution-grid">


            <PollutionCard
              name="PM2.5"
              value={
                data?.pollution?.pm2_5
              }
              unit="µg/m³"
            />


            <PollutionCard
              name="PM10"
              value={
                data?.pollution?.pm10
              }
              unit="µg/m³"
            />


            <PollutionCard
              name="CO"
              value={
                data?.pollution?.co
              }
              unit="µg/m³"
            />


            <PollutionCard
              name="NO₂"
              value={
                data?.pollution?.no2
              }
              unit="µg/m³"
            />


            <PollutionCard
              name="O₃"
              value={
                data?.pollution?.o3
              }
              unit="µg/m³"
            />


            <PollutionCard
              name="SO₂"
              value={
                data?.pollution?.so2
              }
              unit="µg/m³"
            />

          </div>

        </section>



        {/* ==================================================
            CHART
        ================================================== */}

        <section className="section">

          <div className="chart-card">

            <div className="chart-header">

              <p>
                POLLUTION ANALYSIS
              </p>

              <h4>
                {selectedCity} — Pollutant Concentration
              </h4>

            </div>


            <div className="chart-container">

              {chartData.length > 0 ? (

                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >

                  <BarChart
                    data={chartData}
                    margin={{
                      top: 20,
                      right: 10,
                      left: 0,
                      bottom: 10,
                    }}
                  >

                    <CartesianGrid
                      stroke="#dbe4ee"
                      strokeDasharray="4 4"
                    />


                    <XAxis
                      dataKey="name"
                      tick={{
                        fill: "#475569",
                        fontSize: 12,
                      }}
                      axisLine={{
                        stroke: "#cbd5e1",
                      }}
                      tickLine={false}
                    />


                    <YAxis
                      tick={{
                        fill: "#475569",
                        fontSize: 11,
                      }}
                      axisLine={false}
                      tickLine={false}
                    />


                    <Tooltip
                      contentStyle={{
                        background:
                          "#0b1f3a",
                        border: "none",
                        borderRadius:
                          "8px",
                        color:
                          "#ffffff",
                      }}
                      cursor={{
                        fill:
                          "rgba(11,31,58,0.06)",
                      }}
                    />


                    <Bar
                      dataKey="value"
                      fill="#0b1f3a"
                      radius={[
                        5,
                        5,
                        0,
                        0,
                      ]}
                      barSize={45}
                    />

                  </BarChart>

                </ResponsiveContainer>

              ) : (

                <div className="loading-chart">

                  Loading pollution data...

                </div>

              )}

            </div>

          </div>

        </section>



        {/* ==================================================
            CITY COMPARISON
        ================================================== */}

        <section className="section">

          <div className="section-title">

            <h3>
              City Comparison
            </h3>

          </div>


          <div className="city-grid">

            {CITIES.map((city) => {

              const cityResult =
                cityData[city];


              return (

                <button
                  key={city}
                  className={`city-card ${
                    selectedCity === city
                      ? "selected"
                      : ""
                  }`}
                  onClick={() =>
                    selectCity(city)
                  }
                >

                  <div className="city-card-top">

                    <span>

                      <MapPin size={14} />

                      {city}

                    </span>


                    <Cloud size={17} />

                  </div>


                  <strong>

                    {cityResult?.predicted_aqi !==
                    undefined
                      ? Number(
                          cityResult.predicted_aqi
                        ).toFixed(2)
                      : "--"}

                  </strong>


                  <span>

                    {cityResult
                      ? getCategory(
                          cityResult.category
                        )
                      : "Loading..."}

                  </span>


                  <span className="click-text">

                    Click to view details

                  </span>

                </button>

              );

            })}

          </div>

        </section>



        {/* ==================================================
            FOOTER
        ================================================== */}

        <footer className="footer">

          <div>

            <Activity size={14} />

            AQI Intelligence Platform

          </div>


          <div>

            <Navigation size={14} />

            Pakistan

          </div>

        </footer>


      </main>

    </div>
  );
}



function PollutionCard({
  name,
  value,
  unit,
}) {

  return (

    <div className="pollution-card">

      <div>

        <span>
          {name}
        </span>


        <strong>

          {value !== undefined &&
          value !== null
            ? Number(value).toFixed(2)
            : "--"}

        </strong>


        <small>
          {unit}
        </small>

      </div>


      <Wind size={18} />

    </div>

  );

}


export default App;