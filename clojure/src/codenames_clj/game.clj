(ns codenames_clj.game
  (:require   [clojure.java.io :as io]
              [clojure.string :as string]
              [clojure.pprint :as pprint]
              [clojure.set]))
              

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

(defn incorporate-new-pair
  [word-graph [[word association] m-weight]]
  
  (if (not-any? #(clojure.string/includes? word %) (list "-" " "))
    (reduce (fn [graph new-word]
              
              (if (not-any? #(clojure.string/includes? new-word %) (list "(" " " word))
                (update-in graph
                  [word new-word]
                  (fn [counter]
                    ;(println weight)
                    (if counter
                      (+ m-weight counter)
                      m-weight))) 
                graph))
      
      word-graph
      [association])
    word-graph))

(defn reverse-hash
  [model]
  ;(doseq [x (seq (for [item model] (for [word (seq (val item))] [[(key word) (key item)] (val word)])))] 
  ;       (println x)]
  (reduce incorporate-new-pair
    {}
    (seq (for [item model
               x (for [word (seq (val item))] [[(key word) (key item)] (val word)])]
              x))))
             

                    

;(def codenames (range 400))
(defn get-codeword
  "pull from vector of words"
  [num]
  (first (drop num codenames)))

(defn gen-wordlist
  ""
  [number-of-words]
  (let [vv (repeat 25 number-of-words)]
    (vec (map rand-int vv))))
    
 
(defn get-wordlist-words
  "Simply pull words from the list of codenames at random"
  [wl]
  ;(println (vec (doall (map get-codeword wl))))
  (vec (doall (map get-codeword wl))))  


    
      


  

(defn show-gameboard
  "display the words on the board to the player"
  [words]
  ;(println (vec (string/split (slurp codenames-list-file) #"\n")))
  ;(println (partition 5 words))
  ;(println (map keyword (map str (range 5))))
  ;(println (interleave (flatten (repeat 5 (map keyword (map str (range 5))))) words))
  ;(println (apply hash-map (interleave (flatten (repeat 5 (map keyword (map str (range 5)))))  words)))
  ;(println (vec (map #(apply hash-map %) (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 5)))))  words)))))
  ;(println (map string/join " " (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 5))))) words))))
  (pprint/print-table (map keyword (map str (range 1 6))) (vec (doall (map #(apply hash-map %) (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 1 6)))))  words)))))))

(def colors 
  "This definition assumes Red always plays first"
  (flatten (list (repeat 9 "red") (repeat 8 "blue") (repeat 7 "grey") "black")))

(defn assign-words
  [words]
  (apply hash-map (interleave (shuffle words) colors))) 

(defn candidates
  [game-hash compact-model]
  (println (take 5 (vals compact-model)))
  ;(println (seq (reduce #(clojure.set/union %1 %2) (map #(set %) (map #(keys %) (filter #(not (nil? %)) 
                                                                                  ;(map #(compact-model %) 
                                                                                    ;(map #(if (string/starts-with? % "red") %)  
                                                                                      ;(map #(game-hash %) (keys game-hash)))))
  (seq (reduce #(clojure.set/union %1 %2) (map #(set %) (map #(keys %) (filter #(not (nil? %)) 
                                                                         (map #(compact-model %) 
                                                                           (map #(if (string/starts-with? % "red") %)  
                                                                             (map #(game-hash %) (keys game-hash))))))))))

(defn odds
  [clue game-hash compact-model])

(defn make-clue
  [game-hash compact-model])
  
(defn generate-gameboard
  "use game/codewords as default input"
  [words]
  (let [wl1 (gen-wordlist (count words))]
    (let [game-words (get-wordlist-words wl1)]
      ;(let [agents (assign-words game-words)]
        (show-gameboard game-words))))
        ;(show-gameboard (map #(agents %) game-words))
        ;(vec [game-words]))))
    
