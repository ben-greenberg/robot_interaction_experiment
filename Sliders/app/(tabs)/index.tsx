import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Image, TouchableOpacity, ScrollView, TextInput, Platform } from 'react-native';
import Slider from '@mui/material/Slider';  
import { saveAs } from 'file-saver';  

export default function App() {
  const [personName, setPersonName] = useState('');
  const [trialNumber, setTrialNumber] = useState(1);
  const [showWaiting, setShowWaiting] = useState(true);
  const [showNameInput, setShowNameInput] = useState(true);
  const [showEndScreen, setShowEndScreen] = useState(false); 
   
  const [arousal, setArousal] = useState<number>(50);
  const [pleasure, setPleasure] = useState(50);
  const [results, setResults] = useState<string[][]>([]);  

  const handleArousalSliderChange = (event: Event, newValue: number | number[]) => {
    setArousal(newValue as number);
  };

  const handlePleasureSliderChange = (event: Event, newValue: number | number[]) => {
    setPleasure(newValue as number);
  };

  const handleContinue = () => {
    console.log("User is ready to enter metrics.");
    setArousal(50);
    setPleasure(50);
    setShowWaiting(false);
  };

  const handleNameSubmit = () => {
    if (personName.trim() !== '') {
      setShowNameInput(false);
      setShowWaiting(true);
    }

    setStater(1);
    sendStateToBackend(1);
  };
  
  const sendStateToBackend = async (state: any) => {
    console.log(state);
    try {
      const response = await fetch('http://192.168.1.16:3001/api/state', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to send state');
      }
  
      console.log('State sent successfully');
    } catch (error) {
      console.error('Error sending state:', error);
    }
  };


  const appendResults = (newResult: string[]) => {
    setResults(prevResults => [...prevResults, newResult]);
  };

  const handleSubmit = async () => {
    console.log("Trial", trialNumber, "Arousal:", arousal, "Pleasure:", pleasure);
    const data = [trialNumber.toString(), arousal.toString(), pleasure.toString()];  // Convert to strings

    appendResults(data);

    if (trialNumber < 20) {
      setTrialNumber(trialNumber + 1);
      setShowWaiting(true);
    } else {
      endExperiment([...results, data]); 
    }

    setStater(1);
    sendStateToBackend(1);
    
  };

  const [state, setStater] = useState(0);

  const fetchState = async () => {
    try {
      const response = await fetch('http://192.168.1.16:3001/api/state');
      const data = await response.json();

      if (response.ok) {
        console.log(data, "DATA");
        setStater(data.currentState); // Set the state received from the server
        console.log(data.currentState, "EEE");
      } else {
        console.error('Error fetching state:', data.error);
      }
    } catch (error) {
      console.error('Error fetching state:', error);
    }
  };

  const endExperiment = (finalResults: string[][]) => {
    console.log("Experiment completed. Generating CSV.");

    const header = 'Trial,Arousal,Pleasure\n';
    const csvContent = finalResults.map(row => row.join(',')).join('\n');
    const csvData = header + csvContent;

    if (Platform.OS === 'web') {
      // Web Platform File Saving Complete
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `${personName}_Responses.csv`);
    } else {
      // Didn't Do Mobile Platform File Saving Yet, Will Do Later
      console.log("File saving is not implemented for mobile.");
    }

    setShowEndScreen(true);  
    setShowWaiting(false);
  };

  const handleRestart = () => {
    setPersonName('');
    setTrialNumber(1);
    setResults([]);
    setShowNameInput(true);
    setShowEndScreen(false);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      console.log("OIUHBN", state);
      fetchState();
      if (state == 1) {
        fetchState();
      } else if (state === 0) {
        handleContinue();
      }
    }, 1000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [state]);
  
  if (showNameInput) {
    if (state != 0) {
      setStater(0)
      sendStateToBackend(0);
    }
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Enter Your Name</Text>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="PERSON NAME"
            value={personName}
            onChangeText={setPersonName}
            placeholderTextColor="#888"
          />
        </View>
        <TouchableOpacity style={styles.button} onPress={handleNameSubmit}>
          <Text style={styles.buttonText}>Submit</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (showWaiting || state != 0) {
    console.log("WAITING")
    console.log(state);
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Trial #{trialNumber} in Progress</Text>
        <Text style={styles.subtitle}>Please wait to enter your arousal and pleasure metrics</Text>
      </View>
    );
  }

  if (showEndScreen) {
    if (state != 0) {
      // setState(0);
      sendStateToBackend(state);
    }
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Experiment Completed</Text>
        <Text style={styles.subtitle}>Thank you for participating! The results have been saved.</Text>
        <TouchableOpacity style={styles.button} onPress={handleRestart}>
          <Text style={styles.buttonText}>Restart Experiment</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (state == 0) {
  return (
    <ScrollView>
      <View style={styles.container}>
        <Text style={styles.title}>Trial #{trialNumber}</Text>
        <Text style={styles.header}>How Did You Feel During This Situation?</Text>

        <View style={styles.sliderContainer}>
          <Text style={styles.label}>Move The Slider To Rate Your Level Of Arousal</Text>
          <View style={styles.sliderRow}>
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/unaroused.png')} style={styles.icon} />
            <Slider
              value={arousal}
              onChange={handleArousalSliderChange}
              aria-label="Arousal"
              defaultValue={50}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              style={{ color: '#1E90FF' }}
              sx={{
                height: 22,
                width: 1500, 
                '& .MuiSlider-thumb': {
                  width: 33,
                  height: 33, 
                },
              }}
            />
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/aroused.png')} style={styles.icon} />
          </View>
          <View style={styles.gradientIcon}>
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/Slider Gradient.png')} style={styles.gradientImage} />
          </View>
        </View>

        <View style={styles.sliderContainer}>
          <Text style={styles.label}>Move The Slider To Rate Your Level Of Pleasure</Text>
          <View style={styles.sliderRow}>
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/sad.png')} style={styles.icon} />
            <Slider
              value={pleasure}
              onChange={handlePleasureSliderChange}
              aria-label="Pleasure"
              defaultValue={50}
              valueLabelDisplay="auto"
              min={0}
              max={100}
              style={{ color: '#1E90FF' }}
              sx={{
                height: 22, 
                width: 1500, 
                '& .MuiSlider-thumb': {
                  width: 33, 
                  height: 33, 
                },
              }}
            />
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/happy.png')} style={styles.icon} />
          </View>
          <View style={styles.gradientIcon}>
            <Image source={require('C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/Sliders/assets/images/Slider Gradient.png')} style={styles.gradientImage} />
          </View>
        </View>

        <TouchableOpacity style={styles.button} onPress={handleSubmit}>
          <Text style={styles.buttonText}>Submit</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    padding: 30,
  },
  title: {
    fontSize: 50,
    fontWeight: 'bold',
    marginBottom: 40,
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 40,
    color: '#555',
  },
  header: {
    fontSize: 35,
    fontWeight: 'bold',
    marginBottom: 40,
  },
  inputContainer: {
    width: '80%',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  input: {
    width: '100%',
    padding: 10,
    fontSize: 20,
    borderWidth: 1,
    borderRadius: 10,
    borderColor: '#cccccc',
    marginBottom: 20,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#1E90FF',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginTop: 20,
  },
  buttonText: {
    fontSize: 20,
    color: 'white',
    fontWeight: 'bold',
  },
  sliderContainer: {
    marginBottom: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  label: {
    fontSize: 20,
    marginBottom: 20,
    textAlign: 'center',
  },
  sliderRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    width: 50,
    height: 50,
    marginHorizontal: 10,
  },
  gradientIcon: {
    position: 'absolute',
    bottom: -15,
    left: 50,
  },
  gradientImage: {
    width: 1050,
    height: 150,
  },
});
