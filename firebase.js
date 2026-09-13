import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyArvva3d5qqIixi4RUpUzEVO55b_KULjhc",
  authDomain: "gem-compliance-agent-main.firebaseapp.com",
  projectId: "gem-compliance-agent-main",
  storageBucket: "gem-compliance-agent-main.firebasestorage.app",
  messagingSenderId: "306370513406",
  appId: "1:306370513406:web:8205f7209f8acda94a18af",
  measurementId: "G-QH1RG06Z91"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

export { signInWithPopup, signOut };