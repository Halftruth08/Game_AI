(ns codenames-clj.game
  (:require   [clojure.java.io :as io]
              [clojure.string :as string]))

(def number-of-codenames 400)

(def codenames-list-file (io/resource "wordslist.txt"))  

(def codenames  (vec (string/split (slurp codenames-list-file) #"\n")))

(defn entry-words
  [entry]
  
  (flatten (list (key entry) (keys (val entry)))))

(defn compact
  [codenames-list full-model]
   (for [item full-model
         :when (not (not-any? true? (for [word (entry-words item)] (contains? (apply hash-set codenames-list) word))))]
     item))             
              
              

;(def codenames (range 400))
(defn get-codeword
  "pull from vector of words"
  [num]
  (take 1 (drop num codenames)))

(defn gen-wordlist
  ""
  []
  (let [vv (repeat 25 number-of-codenames)]
    (vec (map rand-int vv))))
    
 
(defn get-wordlist-words
  "Simply pull words from the list of codenames at random"
  [wl]
  (vec (map get-codeword wl)))  

(defn generate-gameboard
  ""
  [words])  


  

(defn show-gameboard
  "display the words on the board to the player"
  [words]
  (doseq [row (partition 5 words)]
    (println row)))


