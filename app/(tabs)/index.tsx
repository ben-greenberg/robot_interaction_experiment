import React, { useState } from 'react';
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
    setShowWaiting(false);
  };

  const handleNameSubmit = () => {
    if (personName.trim() !== '') {
      setShowNameInput(false);
      setShowWaiting(true);
    }
  };

  const appendResults = (newResult: string[]) => {
    setResults(prevResults => [...prevResults, newResult]);
  };

  const handleSubmit = () => {
    console.log("Trial", trialNumber, "Arousal:", arousal, "Pleasure:", pleasure);
    const data = [trialNumber.toString(), arousal.toString(), pleasure.toString()];  // Convert to strings

    appendResults(data);

    if (trialNumber < 20) {
      setTrialNumber(trialNumber + 1);
      setShowWaiting(true);
    } else {
      endExperiment([...results, data]); 
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

  if (showNameInput) {
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

  if (showWaiting) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Trial #{trialNumber} in Progress</Text>
        <Text style={styles.subtitle}>Please wait to enter your arousal and pleasure metrics</Text>
        <TouchableOpacity style={styles.button} onPress={handleContinue}>
          <Text style={styles.buttonText}>Continue</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (showEndScreen) {
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

  return (
    <ScrollView>
      <View style={styles.container}>
        <Text style={styles.title}>Trial #{trialNumber}</Text>
        <Text style={styles.header}>How Did You Feel During This Situation?</Text>

        <View style={styles.sliderContainer}>
          <Text style={styles.label}>Move The Slider To Rate Your Level Of Arousal</Text>
          <View style={styles.sliderRow}>
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/unaroused.png')} style={styles.icon} />
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
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/aroused.png')} style={styles.icon} />
          </View>
          <View style={styles.gradientIcon}>
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/Slider Gradient.png')} style={styles.gradientImage} />
          </View>
        </View>

        <View style={styles.sliderContainer}>
          <Text style={styles.label}>Move The Slider To Rate Your Level Of Pleasure</Text>
          <View style={styles.sliderRow}>
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/sad.png')} style={styles.icon} />
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
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/happy.png')} style={styles.icon} />
          </View>
          <View style={styles.gradientIcon}>
            <Image source={require('/Users/likhith/Desktop/RAM LAB Programs/ArousalPleasureSliders/assets/images/Slider Gradient.png')} style={styles.gradientImage} />
          </View>
        </View>

        <TouchableOpacity style={styles.button} onPress={handleSubmit}>
          <Text style={styles.buttonText}>Submit</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
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
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    textAlign: 'center', 
  },
  sliderContainer: {
    width: '100%',
    marginBottom: 40,
  },
  label: {
    fontSize: 20,
    marginBottom: 10,
    textAlign: 'center',
  },
  sliderRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  slider: {
    flex: 5,
    height: 40,
    marginHorizontal: 10,
  },
  icon: {
    width: 70,
    height: 70,
    marginHorizontal: 10,
  },
  gradientIcon: {
    width: '100%',
    alignItems: 'center',
    marginBottom: 40,
  },
  gradientImage: {
    width: '90%', 
    height: 92.5,
    resizeMode: 'contain', 
  },
  button: {
    backgroundColor: '#1E90FF',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
});
