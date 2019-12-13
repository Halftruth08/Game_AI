(ns codenames_clj.core
  (:require [clojure.java.io :as io]
            [clojure.string :as string]
            [codenames_clj.model :as mdl]
            [codenames_clj.storage :as store]
            [codenames_clj.game :as game]
            [codenames_clj.ux :as ux])
  (:gen-class))


(def win (atom 0))
(def lose (atom 0))

;(def model1 (io/resource "models/model1.txt"))

(defn wincond
  ""
  []
  (println "You WON!"))

(defn losecond
  ""
  []
  (println "You LOST!"))

(defn colorstate
  ""
  [color tagents]
  (if (string/starts-with? color "blue")
    (if (< (count (remove #(not (string/starts-with? % "blue")) (vals tagents))) 2)
      (swap! lose inc))
    (if (string/starts-with? color "red")
      (if (< (count (remove #(not (string/starts-with? % "red")) (vals tagents))) 2)
        (swap! win inc))
      (if (string/starts-with? color "black")
        (swap! lose inc)))))
(defn subt-1
  ""
  [val1]
  [(first val1) (- (last val1) 1)])
  

(defn subt-guess
  ""
  [clue]
  (println clue)
  (if (= (last clue) 1) [] [(first clue) (- (last clue) 1)]))

(defn cluechange
  ""
  [color clue]
  (if (string/starts-with? color "red") 
    (subt-guess clue)
    []))
    ;(dissoc (first (keys clue)))))
(defn new-cds
  "enforce non-repeating clues"
  [cds clue]
  (remove #(and (string/starts-with? % (first clue))
                (string/ends-with? % (first clue))) cds))

(defn colorstate2
  ""
  [color tagents]
  (println color))
  

(defn redf
  ""
  [tagents]
  (if (< (remove #(not (string/starts-with? % "red")) (vals tagents)) 2)
    (swap! win 1)))
  
(defn greyf
  ""
  [tagents])
  
(defn blackf
  ""
  [tagents]
  (swap! lose 1))

(defn play
  "Need to add: different function for different players"
  [player]
  (reset! lose 0)
  (reset! win 0)
  ;(println "begin play")
  (let [wl1 (game/gen-wordlist (count game/codenames))]
    (let [game-words (game/get-wordlist-words wl1)]
      ;(println "debug 1")
      (let [agents (game/assign-words game-words)
            mod1 (if (.exists (io/as-file "resources/models/model1b.txt")) 
                   (mdl/generate-all-models [["models/model1b.txt" 1]]) 
                   mdl/model)
            out (string/join [player "_log.txt"])]
        ;(println mod1)
        ;(game/show-gameboard game-words)
          
          (loop [tagents agents
                 pass-clue []
                 cds (game/candidates agents mod1)
                 mout (if (.exists (io/as-file (string/join ["resources/models/" out]))) (mdl/generate-all-models [[(string/join ["models/" out]) 1]]) {})]
            ;(println "debug 2.5")
            (def mmout mout)
            (def frm (ux/window "" ""))
            ;(println "debug 3")
            (when (and (zero? @lose) (zero? @win))
              (let [twords (game/remaining agents tagents game-words)]
                (game/show-gameboard twords)
                ;(println "debug 4")
                ;(println cds)
                (let [nets (map #(game/nets % tagents mod1) (remove #(contains? tagents %) cds))]
                  ;(println nets)
                  ;(println (map #(game/odds %1 %2) cds nets))))
                  ;(let [clues (reduce conj {} (map #(game/odds %1 %2) cds nets))]
                   (let [clue (game/what-clue cds nets pass-clue)] 
                    (game/give-clue clue)
                    ;(println (first (sort > (keys clues))) (first (map #(clues %) (sort > (keys clues)))))
                    (let [guess-word (->> (game/safe-read-line tagents twords)
                                          (game/guess2word)
                                          (nth twords))
                          ;(nth twords (game/guess2word (game/safe-read-line tagents twords)))
                          ]
                      ;(println (tagents guess-word))
                      (-> tagents
                          (get guess-word)
                          (colorstate tagents))
                      ;(colorstate (get tagents guess-word) tagents)
                      ;(println (string/join #"|" [(first clue) (str (count (keys tagents)))]))
                      ;
                      ;(println  (str guess-word)
                      (recur (game/execute tagents guess-word)
                             (cluechange (get tagents guess-word) clue)
                             (new-cds cds clue)
                             (mdl/incorporate-new-line mout [[(string/join #"|" (->> (keys tagents)
                                                                                     count
                                                                                     str
                                                                                     (conj [(first clue)]))) (str guess-word)] 1]))))))))
          (if (pos? @win) (wincond))
          (if (pos? @lose) (losecond))
        (store/model-save out mmout)
        (->> game-words
             (map #(agents %))
             (game/show-gameboard))
        ))))

(defn modelgamut
  "build lots of models"
  [& args]
  (if (.exists (io/as-file "resources/models/test.txt"))
    (println "test.txt exists")
    (store/model-save "test.txt" []))
  (let [mod1 (if (.exists (io/as-file "resources/models/model1.txt"))
               (mdl/generate-all-models [["models/model1.txt" 1]])
               mdl/model)
        out "resources/models/test.txt"]
    (println (type mod1))
    (doseq [x (take 5 mod1)] (game/entry-words x))
    (doseq [x (take 5 (keys mod1))] (println x))
    (doseq [x (take 5 (keys (first (vals mod1))))] (println x))
    (println (type (first (vals mod1))))
    (def modc (game/compact game/codenames mod1))
    (doseq [x (take 1 modc)] (println x))
    (def modr (game/reverse-hash modc))
    (doseq [x (take 1 modr)] (println x))
    (def modrc (game/compact game/codenames modr))
    (doseq [x (take 1 modrc)] (println x))
    (println (store/entry "word" "weight" "leaf"))
    (spit out (string/join "\n" (take 5 (keys (first (vals mod1)))))))
  (if (.exists (io/as-file "resources/models/model1c.txt"))
    (doseq [x (take 1 modc)] (println x))
    (store/model-save "model1c.txt" modc))
  (if (.exists (io/as-file "resources/models/model1r.txt"))
    (doseq [x (take 1 modr)] (println x))
    (store/model-save "model1r.txt" modr))
  (if (.exists (io/as-file "resources/models/model1rc.txt"))
    (doseq [x (take 1 modrc)] (println x))
    (store/model-save "model1rc.txt" modrc))
  (let [modb (mdl/generate-all-models [["models/model1c.txt" 1]
                                       ["models/model1rc.txt" 1]])]
    (doseq [x (take 5 modb)] (println x))
    (if (.exists (io/as-file "resources/models/model1b.txt"))
      (doseq [x (take 5 modb)] (println x))
      (store/model-save "model1b.txt" modb)))
  (store/model-save "model1.txt" mdl/model)
  (println (first mdl/model-files)))
  
(defn -main
  "I now play a game with you and remember your answers"
  [& args]
  (println "Hello, World!")
  ;(ux/popopen "Hello, User!" "Nice to meet you!")
  (if  (.exists (io/as-file "resources/models/model1b.txt"))
    (println "model1b.txt exists")
    (modelgamut))
  (play "human"))

  
  ;(game/generate-gameboard game/codenames)
  ;(println codenames-get)
  ;(println (vec (repeat 25 number-of-codenames)))
  ;(let [wl1 (game/gen-wordlist)]
  ;(println wl1)
  ;(println (- 9 1))
  ;(println (game/get-wordlist-words wl1))
  ;(println (subvec (get-wordlist-words wl1) 0 5))
  ;(game/show-gameboard (game/get-wordlist-words wl1))
  ;(println (first mdl/model-files))
  ;(doseq [x (take 25 (mdl/model))] (println x))

