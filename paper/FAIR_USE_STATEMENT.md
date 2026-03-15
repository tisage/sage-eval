# Fair Use Statement for Academic Research

## 📄 For Inclusion in AAAI 2025 Paper

### Ethical Statement (LaTeX)

```latex
\section*{Ethical Statement}

This research analyzes 75 literary short stories to evaluate the SAGE (Six-layer Automated Generative Evaluation) framework. The corpus includes:

\begin{itemize}
    \item \textbf{62 public domain works}: Authors deceased >70 years or published >95 years ago, freely available from Project Gutenberg, Wikisource, and Internet Archive.
    \item \textbf{13 copyrighted works}: Used under Fair Use provisions (17 U.S.C. \S 107) for non-commercial academic research and computational literary analysis.
\end{itemize}

\subsection*{Fair Use Justification}

The use of copyrighted works is transformative and falls within Fair Use doctrine under the following criteria:

\begin{enumerate}
    \item \textbf{Purpose and Character}: Non-commercial academic research presented at AAAI 2025. The analysis is transformative, converting literary texts into quantitative evaluation scores across six linguistic and cultural dimensions.

    \item \textbf{Nature of the Work}: Published literary works analyzed for scholarly purposes, consistent with established practices in computational literary studies and digital humanities.

    \item \textbf{Amount and Substantiality}: Complete short stories are necessary for comprehensive multi-layer evaluation. Similar to text mining research (Authors Guild v. HathiTrust, 755 F.3d 87, 2014), full-text analysis is essential for valid computational analysis.

    \item \textbf{Effect on Market}: No market substitution occurs. Research outputs consist of evaluation scores and statistical analyses, not reproduction of original texts. No texts are redistributed publicly.
\end{enumerate}

\subsection*{Precedent}

This usage aligns with Fair Use precedents in computational text analysis:
\begin{itemize}
    \item \textit{Authors Guild v. HathiTrust} (2014): Full-text scanning for research purposes ruled Fair Use
    \item \textit{Authors Guild v. Google} (2015): Book digitization for searchable database ruled Fair Use
    \item Digital Humanities text mining practices (e.g., Stanford Literary Lab, HathiTrust Research Center)
\end{itemize}

All copyrighted works are properly attributed with bibliographic citations. No copyrighted texts are included in supplementary materials or publicly distributed datasets.
```

---

### Plain English Statement

**For Ethics/Data Availability Section:**

> This study uses 75 literary short stories for evaluation. 62 works are in the public domain and freely available. 13 copyrighted works (by Borges, Cortázar, Kawabata, Shen Congwen, and Nakajima) are used under Fair Use (17 U.S.C. § 107) for non-commercial computational literary analysis. These works are analyzed locally and not redistributed. Our research outputs consist of evaluation scores and statistical analyses, constituting transformative use consistent with Fair Use precedent in digital humanities (Authors Guild v. HathiTrust, 2014; Authors Guild v. Google, 2015). All works are properly cited.

---

## 📚 Bibliography Entries

### Copyrighted Works Used Under Fair Use

```bibtex
% Jorge Luis Borges
@incollection{borges1962south,
  title={The South},
  author={Borges, Jorge Luis},
  booktitle={Ficciones},
  translator={Kerrigan, Anthony},
  year={1962},
  publisher={Grove Press},
  address={New York},
  note={Originally published 1953. Used under Fair Use for academic research.}
}

@incollection{borges1970aleph,
  title={The Aleph},
  author={Borges, Jorge Luis},
  booktitle={The Aleph and Other Stories},
  translator={di Giovanni, Norman Thomas},
  year={1970},
  publisher={Dutton},
  address={New York},
  note={Originally published 1945. Used under Fair Use for academic research.}
}

@incollection{borges1962funes,
  title={Funes the Memorious},
  author={Borges, Jorge Luis},
  booktitle={Ficciones},
  translator={Kerrigan, Anthony},
  year={1962},
  publisher={Grove Press},
  note={Originally published 1942. Used under Fair Use for academic research.}
}

@incollection{borges1970zahir,
  title={The Zahir},
  author={Borges, Jorge Luis},
  booktitle={The Aleph and Other Stories},
  translator={di Giovanni, Norman Thomas},
  year={1970},
  publisher={Dutton},
  note={Originally published 1949. Used under Fair Use for academic research.}
}

% Julio Cortázar
@incollection{cortazar1967house,
  title={House Taken Over},
  author={Cort{\'a}zar, Julio},
  booktitle={Blow-Up and Other Stories},
  translator={Blackburn, Paul},
  year={1967},
  publisher={Pantheon Books},
  note={Originally published 1946. Used under Fair Use for academic research.}
}

@incollection{cortazar1967axolotl,
  title={Axolotl},
  author={Cort{\'a}zar, Julio},
  booktitle={Blow-Up and Other Stories},
  translator={Blackburn, Paul},
  year={1967},
  publisher={Pantheon Books},
  note={Originally published 1952. Used under Fair Use for academic research.}
}

% Yasunari Kawabata
@book{kawabata1955izu,
  title={The Izu Dancer and Other Stories},
  author={Kawabata, Yasunari},
  year={1955},
  publisher={Charles E. Tuttle Company},
  note={Originally published 1926. Used under Fair Use for academic research.}
}

@book{kawabata1996snow,
  title={Snow Country},
  author={Kawabata, Yasunari},
  translator={Seidensticker, Edward G.},
  year={1996},
  publisher={Vintage International},
  note={Originally published 1935. Excerpt used under Fair Use for academic research.}
}

% Shen Congwen
@book{shen2009border,
  title={Border Town},
  author={Shen, Congwen},
  translator={King, Gladys Yang},
  year={2009},
  publisher={HarperCollins},
  note={Originally published 1934. Excerpt used under Fair Use for academic research.}
}

% Atsushi Nakajima
@incollection{nakajima1992moon,
  title={Moon Over the Mountain},
  author={Nakajima, Atsushi},
  booktitle={Japanese Literature Today},
  year={1992},
  note={Originally published 1942. Used under Fair Use for academic research.}
}
```

---

## 🔒 Data Management Plan

### Storage and Access

1. **Local Storage Only**
   - Copyrighted works stored in `data/corpus/fair_use/`
   - Directory excluded from Git via `.gitignore`
   - No cloud backup of copyrighted files

2. **Access Control**
   - Files accessible only to research team
   - Not shared via email, cloud storage, or public repositories
   - Evaluation outputs (scores) can be shared; original texts cannot

3. **Publication**
   - Research paper includes statistical results only
   - No full texts in supplementary materials
   - Brief quotations (<300 words) only, with proper attribution

---

## ✅ Compliance Checklist

Before submission to AAAI 2025:

- [ ] Ethical statement included in paper
- [ ] All 13 copyrighted works properly cited in bibliography
- [ ] Fair Use justification clearly stated
- [ ] No copyrighted texts in supplementary materials
- [ ] Evaluation outputs do not reproduce original texts
- [ ] Public domain works clearly distinguished from fair use works
- [ ] Data availability statement clarifies which works are publicly accessible

---

## 📞 Contact for Questions

If reviewers or editors have questions about Fair Use compliance:

**Principal Investigator**: [Your Name]
**Institution**: [Your University]
**Email**: [Your Academic Email]

**Fair Use Resources**:
- Stanford Copyright & Fair Use Center: https://fairuse.stanford.edu
- Association of Research Libraries Code of Best Practices: https://www.arl.org/code-of-best-practices/

---

**Last Updated**: 2025-11-23
